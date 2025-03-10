import os
import sys
import argparse
import ctypes
import logging
import time

from watchdog.events import FileSystemEventHandler
import winshell

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filename='uproject-autoshortcut.log'
)


class UProjectHandler(FileSystemEventHandler):
    def __init__(self, root_dir, start_menu_dir):
        self.root_dir = root_dir
        self.start_menu_dir = start_menu_dir
        self.logger = logging.getLogger('UProjectHandler')
        self.logger.setLevel(logging.INFO)

    def on_created(self, event):
        try:
            if event.is_directory:
                self.logger.info(f"Detected new directory: {event.src_path}")
                self.process_project(event.src_path, create=True)
        except Exception as e:
            self.logger.error(f"Error handling creation event: {str(e)}")

    def on_deleted(self, event):
        try:
            if event.is_directory:
                self.logger.info(f"Detected deleted directory: {event.src_path}")
                self.delete_shortcut(os.path.basename(event.src_path))
        except Exception as e:
            self.logger.error(f"Error handling deletion event: {str(e)}")

    def on_moved(self, event):
        try:
            if event.is_directory:
                self.logger.info(f"Detected moved directory: {event.src_path} -> {event.dest_path}")
                self.delete_shortcut(os.path.basename(event.src_path))
                self.process_project(event.dest_path, create=True)
        except Exception as e:
            self.logger.error(f"Error handling move event: {str(e)}")

    def process_project(self, project_path, create=False):
        try:
            project_name = os.path.basename(project_path)
            uproject_file = os.path.join(project_path, f"{project_name}.uproject")

            if os.path.exists(uproject_file):
                if create:
                    self.logger.info(f"Creating shortcut for {project_name}")
                    self.create_shortcut(project_path)
            else:
                self.logger.info(f"No .uproject file found in {project_path}")
                self.delete_shortcut(project_name)
        except Exception as e:
            self.logger.error(f"Error processing project: {str(e)}")

    def create_shortcut(self, project_path):
        try:
            import pythoncom
            pythoncom.CoInitialize()

            project_name = os.path.basename(project_path)
            shortcut_path = os.path.join(self.start_menu_dir, f"{project_name}.lnk")
            uproject_file = os.path.join(project_path, f"{project_name}.uproject")

            if not os.path.exists(shortcut_path):
                with winshell.shortcut(shortcut_path) as shortcut:
                    shortcut.path = uproject_file
                    shortcut.description = f"Unreal Project: {project_name}"
                    shortcut.working_directory = project_path
                self.logger.info(f"Created shortcut: {shortcut_path}")
        except Exception as e:
            self.logger.error(f"Error creating shortcut: {str(e)}")
        finally:
            pythoncom.CoUninitialize()

    def delete_shortcut(self, project_name):
        try:
            shortcut_path = os.path.join(self.start_menu_dir, f"{project_name}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                self.logger.info(f"Deleted shortcut: {shortcut_path}")
        except Exception as e:
            self.logger.error(f"Error deleting shortcut: {str(e)}")


def get_start_menu_dir(folder_name):
    base_dir = os.path.join(
        os.environ['APPDATA'],
        'Microsoft',
        'Windows',
        'Start Menu',
        'Programs'
    )
    target_dir = os.path.join(base_dir, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def initial_sync(root_dir, start_menu_dir):
    logger = logging.getLogger('InitialSync')
    logger.setLevel(logging.INFO)

    try:
        # Create shortcuts for existing projects
        logger.info("Starting initial sync")
        for dir_name in os.listdir(root_dir):
            dir_path = os.path.join(root_dir, dir_name)
            if os.path.isdir(dir_path):
                handler = UProjectHandler(root_dir, start_menu_dir)
                handler.process_project(dir_path, create=True)

        # Remove orphaned shortcuts
        for lnk_name in os.listdir(start_menu_dir):
            if lnk_name.endswith('.lnk'):
                project_name = lnk_name[:-4]
                project_path = os.path.join(root_dir, project_name)
                if not os.path.exists(project_path):
                    shortcut_path = os.path.join(start_menu_dir, lnk_name)
                    try:
                        os.remove(shortcut_path)
                        logger.info(f"Removed orphaned shortcut: {lnk_name}")
                    except Exception as e:
                        logger.error(f"Error removing orphaned shortcut: {str(e)}")
        logger.info("Initial sync completed")
    except Exception as e:
        logger.error(f"Initial sync failed: {str(e)}")


def hide_console():
    if sys.platform == 'win32':
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def main():
    parser = argparse.ArgumentParser(description='Unreal Project Shortcut Manager')
    parser.add_argument('--root', required=True, help='Root directory to watch')
    parser.add_argument('--folder', required=True, help='Start Menu folder name for shortcuts')
    parser.add_argument('--daemon', action='store_true', help='Run in background mode')
    args = parser.parse_args()

    try:
        if not os.path.isdir(args.root):
            raise FileNotFoundError(f"Directory {args.root} does not exist")

        start_menu_dir = get_start_menu_dir(args.folder)
        initial_sync(args.root, start_menu_dir)

        if args.daemon:
            logging.info("Starting daemon mode")
            if sys.platform == 'win32':
                hide_console()

            event_handler = UProjectHandler(args.root, start_menu_dir)

            # Try alternative observer for network drives
            try:
                from watchdog.observers.polling import PollingObserver
                observer = PollingObserver()  # Slower but more reliable
                logging.info("Using polling observer")
            except ImportError:
                from watchdog.observers import Observer
                observer = Observer()  # Default observer
                logging.info("Using default observer")

            observer.schedule(event_handler, args.root, recursive=False)
            observer.start()
            logging.info(f"Started watching directory: {args.root}")

            try:
                while True:
                    # Verify observer status periodically
                    if not observer.is_alive():
                        logging.error("Observer thread died! Restarting...")
                        observer = Observer()
                        observer.schedule(event_handler, args.root, recursive=False)
                        observer.start()
                    time.sleep(5)
            except KeyboardInterrupt:
                observer.stop()
                observer.join()

            logging.info("Daemon stopped")

    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()