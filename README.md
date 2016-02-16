# HipScud - Linux Client app for HipChat

HipScud is a **non official** open-source Linux (Debian, Ubuntu, Kubuntu, Mint, Arch, Fedora) desktop client app for [HipChat](http://hipchat.com) based on [ScudCloud for Slack](https://github.com/raelgc/scudcloud).

HipScud improves the HipChat integration with Linux desktops featuring:

* multiple teams support
* supports HipChat connect & most other features that HipChat for Mac/Windows supports but Linux doesn't
* count of unread direct mentions at launcher/sytray icon
* alert/wobbling on new messages
* channels quicklist (Unity only)
* optional tray notifications and "Close to Tray"

# Install

## Manual Install

The manual install is intended for not supported distros (if you want to contribute with a package for your distro, you're welcome!).

First, you'll need to install at least packages for `python3`, `python-qt4` (`qt4` for `python3`) and `python-dbus` (`dbus` library for `python3`).

HipScud can be run from the development tree. Simply run the following from the root of the project tree:

```bash
python3 -m hipscud
```

# Troubleshooting

#### 1. Default domain and loading order

You can change the default domain (or the domain loading order) editing or just deleting the config file:

    ~/.config/hipscud/hipscud.cfg

#### 2. Where is the package for my distro?

If not listed above, you're welcome [to contribute](/CONTRIBUTING.md). In this meanwhile, try the [Manual Install](#manual-install) instructions.

#### 3. Spell checking is not working

Make sure you have the following packages installed:

* `libqtwebkit-qupzillaplugins`
* `python3-hunspell`
* `hunspell-en-us`

#### 4. `Keep me signed in` is not working / My team is not saved

For some reason, HipScud was not able to create the configuration folder. Please, manually create this folder:

    mkdir -p ~/.config/hipscud/
    
If it exists and `.cfg` file is present, try change permissions in config file:

    chmod -R 0755 ~/.config/hipscud/hipscud.cfg

#### 5. How to start HipScud minimized?

You can start HipScud minized to tray with:

    hipscud --minimized=True

#### 6. High DPI Support

HipScud offers zoom support. The zoom level will be persisted between sessions.

- Increase zoom pressing <kbd>Ctrl +</kbd>, usually fired with <kbd>Ctrl Shift =</kbd>
- Decrease with <kbd>Ctrl -</kbd>
- Reset it with <kbd>Ctrl 0</kbd>

#### 7. No icon in systray/notification area

Make sure that `File` > `Close to Tray` is checked.

# License

HipScud is is released under the [MIT License](/LICENSE).
