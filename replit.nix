{pkgs}: {
  deps = [
    pkgs.geckodriver
    pkgs.xvfb-run
    pkgs.scrot
    pkgs.postgresql
    pkgs.openssl
  ];
}
