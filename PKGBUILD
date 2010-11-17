# Contributor: Ben Morgan <benm.morgan@gmail.com>
pkgname=moped
pkgver=2.15b1
pkgrel=3
pkgdesc="Moped is an advanced and flexible tool to manipulate MPD playlists"
arch=('any') # I haven't tested x86_64
url=""
license=('GPL')
groups=()
depends=("python>=3.1.2" zenity mpd)
makedepends=()
provides=()
conflicts=()
replaces=()
backup=()
install=
source=(https://github.com/downloads/cassava/Moped/$pkgname-$pkgver.tar.gz)
noextract=()

build() {
  cd $srcdir/$pkgname-$pkgver
  
  mv install.sh.example install.sh
  chmod +x install.sh
  ./install.sh $pkgdir
  
  #ln -s /usr/lib/moped/moped.py $pkgdir/usr/bin/moped
}
md5sums=('eee2cb4960186cba53c905f485ccb885')
