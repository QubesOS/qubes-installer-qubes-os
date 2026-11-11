# Qubes OS installer (obsolete)

This repository is obsolete and is not used by
[qubes-builderv2](https://github.com/QubesOS/qubes-builderv2).

It built the Qubes OS installer ISO with the legacy
[qubes-builder](https://github.com/QubesOS/qubes-builder): kickstart files,
package groups (comps), and the scripts that ran `lorax` to make the ISO.

In qubes-builderv2 this is split up:

- the ISO is built by the builder's own `installer` plugin;
- the kickstart files and comps are in
  [qubes-qubes-release](https://github.com/QubesOS/qubes-qubes-release);
- the installer parts are separate components:
  [qubes-anaconda](https://github.com/QubesOS/qubes-anaconda),
  [qubes-anaconda-addon](https://github.com/QubesOS/qubes-anaconda-addon),
  [qubes-lorax-templates](https://github.com/QubesOS/qubes-lorax-templates),
  [qubes-pykickstart](https://github.com/QubesOS/qubes-pykickstart) and
  [qubes-blivet](https://github.com/QubesOS/qubes-blivet).

For how to install Qubes OS, see the
[installation guide](https://www.qubes-os.org/doc/installation-guide/).
