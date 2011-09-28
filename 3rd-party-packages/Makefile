rpms:
	./nvidia_build.sh
	# Sign all rpms - also this just downloaded
	# (dom0 has no keys to verify original signature)
	rpm --addsign rpm/x86_64/*.rpm

clean:
	rm *.src.rpm
	rm -rf rpm/
