from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, SystemExitEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

import subprocess

from memoization import cached

ACTIVATE_COMMAND = 'xdotool windowactivate {}'

@cached(ttl=15)
def get_window_name(window_id):
    proc = subprocess.Popen(['xdotool', 'getwindowname', window_id],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()    
    out = stdout.decode().strip()
    return out
def get_xprop(window_id, class_name):
    # class="WM_CLASS|_NET_WM_PID"
    proc = subprocess.Popen(['xprop', '-id', window_id, class_name],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()    
    out = stdout.decode().strip()
    return out

@cached(ttl=5)
def list_windows():
    """List the windows being managed by the window manager.

    Returns:
        list -- with dict for each window entry:
                'name': window name
                'id': window ID
    """
    windows=[]
    proc = subprocess.Popen(['xdotool', 'search', '--onlyvisible', '--name', ''],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    out = stdout.decode().strip()

    # Search for a window by name or class
    for window_id in out.splitlines():
        try:
            window_name = get_window_name(window_id)
            if window_name == "": continue
            windows.append({
                'name': window_name,
                'id': window_id,
                'window_class': get_xprop(window_id, 'WM_CLASS'),
                'pid': get_xprop(window_id, '_NET_WM_PID')
                })
        except Exception as e:
            print("[ERROR] {}".format(e))
            pass

    return windows


@cached(ttl=15)
def get_process_name(pid):
    """Find out process name, given its' ID

    Arguments:
        pid {int} -- process ID
    Returns:
        str -- process name
    """
    proc = subprocess.Popen(['ps', '-p', pid, '-o', 'comm='],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err=proc.communicate()
    return out.strip().decode('utf-8').lower()


def get_open_windows():
    """Get open windows

    Returns:
        List[ExtensionResultItem] -- list of Ulauncher result items
    """
    windows=list_windows()
    # Filter out stickies (desktop is -1)
    # non_stickies=filter(lambda x: x['desktop'] != '-1', windows)
    non_stickies=windows

    results = []
    for window in non_stickies:
        results.append(ExtensionResultItem(icon='images/icon.png',
                                           name=str(window['name']),
                                           description=str(window['name']),
                                           on_enter=RunScriptAction(ACTIVATE_COMMAND.format(window['id']), None)
                       ))
    return results


class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(SystemExitEvent, SystemExitEventListener())
        self.windows = []


class SystemExitEventListener(EventListener):
    def on_event(self, event, extension):
        pass

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        windows = get_open_windows()
        extension.windows = windows  # persistance

        arg = event.get_argument()
        if arg is not None:
            # filter by title or process name
            windows = filter(lambda x: arg in x.get_name().lower() or arg in x.get_description(None).lower(),
                             windows)

        return RenderResultListAction(list(windows))


if __name__ == '__main__':
    DemoExtension().run()
