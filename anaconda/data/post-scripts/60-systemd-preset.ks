%post

# preset all services, to not worry about package installation order (preset
# files vs services)
systemctl preset-all

systemctl enable initial-setup.service

%end
