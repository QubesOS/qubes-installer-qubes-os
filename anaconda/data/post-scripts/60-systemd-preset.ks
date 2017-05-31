%post

# preset all services, to not worry about package installation order (preset
# files vs services)
systemctl preset-all

systemctl enable initial-setup.service

# systemctl preset-all disables default target
# (https://bugzilla.redhat.com/1316387), re-enable it manually
systemctl set-default graphical.target

%end
