#  Copyright (C) 2016 - Yevgen Muntyan
#  Copyright (C) 2016 - Ignacio Casal Quinteiro
#  Copyright (C) 2016 - Arnavion
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.

import glob
import os

from gvsbuild.utils.base_builders import MakeGir, Meson
from gvsbuild.utils.base_expanders import Tarball
from gvsbuild.utils.base_project import Project, project_add


class Project_gtk_base(Tarball, Project, MakeGir):
    def make_all_mo(self):
        mo = "gtk20.mo" if self.name == "gtk" else "gtk30.mo"

        localedir = os.path.join(self.pkg_dir, "share", "locale")
        self.push_location(r".\po")
        for fp in glob.glob(os.path.join(self.build_dir, "po", "*.po")):
            f = os.path.basename(fp)
            lcmsgdir = os.path.join(localedir, f[:-3], "LC_MESSAGES")
            self.builder.make_dir(lcmsgdir)
            cmd = " ".join(["msgfmt", "-co", os.path.join(lcmsgdir, mo), f])
            self.builder.exec_cmd(cmd, working_dir=self._get_working_dir())
        self.pop_location()

        self.install(r".\COPYING share\doc\%s" % self.name)


@project_add
class Gtk(Project_gtk_base):
    def __init__(self):
        Project.__init__(
            self,
            "gtk",
            archive_url="http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/2.24/gtk+-2.24.31.tar.xz",
            hash="68c1922732c7efc08df4656a5366dcc3afdc8791513400dac276009b40954658",
            dependencies=["atk", "gdk-pixbuf", "pango"],
            patches=[
                "gtk-revert-scrolldc-commit.patch",
                "gtk-bgimg.patch",
                "gtk-accel.patch",
                # https://github.com/hexchat/hexchat/issues/1007
                "gtk-multimonitor.patch",
                # These two will be in 2.24.33
                "bfdac2f70e005b2504cc3f4ebbdab328974d005a.patch",
                "61162225f712df648f38fd12bc0817cfa9f79a64.patch",
                # https://github.com/hexchat/hexchat/issues/2077
                "0001-GDK-W32-Remove-WS_EX_LAYERED-from-an-opaque-window.patch",
            ],
        )
        if Project.opts.enable_gi:
            self.add_dependency("gobject-introspection")

    def build(self):
        self.builder.mod_env(
            "INCLUDE", "{}\\include\\harfbuzz".format(self.builder.gtk_dir)
        )
        self.exec_msbuild_gen(r"build\win32", "gtk+.sln", add_pars="/p:UseEnv=True")

        self.make_all_mo()

    def post_install(self):
        if Project.opts.enable_gi:
            self.builder.mod_env(
                "INCLUDE", "{}\\include\\cairo".format(self.builder.gtk_dir)
            )
            self.builder.mod_env(
                "INCLUDE", "{}\\include\\harfbuzz".format(self.builder.gtk_dir)
            )
            self.make_single_gir("gtk", prj_dir="gtk")


@project_add
class Gtk320(Project_gtk_base):
    def __init__(self):
        if self.opts.gtk3_ver != "3.20":
            self.ignore()
            return

        Project.__init__(
            self,
            "gtk3",
            prj_dir="gtk3-20",
            archive_url="http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/3.20/gtk+-3.20.10.tar.xz",
            hash="e81da1af1c5c1fee87ba439770e17272fa5c06e64572939814da406859e56b70",
            dependencies=["atk", "gdk-pixbuf", "pango", "libepoxy"],
            patches=["gtk3-clip-retry-if-opened-by-others.patch"],
        )
        if Project.opts.enable_gi:
            self.add_dependency("gobject-introspection")

    def build(self):
        self.builder.mod_env(
            "INCLUDE", "{}\\include\\harfbuzz".format(self.builder.gtk_dir)
        )
        self.exec_msbuild_gen(
            r"build\win32", "gtk+.sln", add_pars="/p:UseEnv=True /p:GtkPostInstall=rem"
        )

        self.make_all_mo()

    def post_install(self):
        if Project.opts.enable_gi:
            self.builder.mod_env(
                "INCLUDE", "{}\\include\\cairo".format(self.builder.gtk_dir)
            )
            self.make_single_gir("gtk", prj_dir="gtk3-20")

        self.exec_cmd(
            r"%(gtk_dir)s\bin\glib-compile-schemas.exe %(gtk_dir)s\share\glib-2.0\schemas"
        )
        self.exec_cmd(
            r'%(gtk_dir)s\bin\gtk-update-icon-cache.exe --ignore-theme-index --force "%(gtk_dir)s\share\icons\hicolor"'
        )


@project_add
class Gtk322(Project_gtk_base):
    def __init__(self):
        if self.opts.gtk3_ver != "3.22":
            self.ignore()
            return

        Project.__init__(
            self,
            "gtk3",
            prj_dir="gtk3-22",
            archive_url="http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/3.22/gtk+-3.22.30.tar.xz",
            hash="a1a4a5c12703d4e1ccda28333b87ff462741dc365131fbc94c218ae81d9a6567",
            dependencies=["atk", "gdk-pixbuf", "pango", "libepoxy"],
        )
        if Project.opts.enable_gi:
            self.add_dependency("gobject-introspection")

    def build(self):
        self.builder.mod_env(
            "INCLUDE", "{}\\include\\harfbuzz".format(self.builder.gtk_dir)
        )
        self.exec_msbuild_gen(
            r"build\win32", "gtk+.sln", add_pars="/p:UseEnv=True /p:GtkPostInstall=rem"
        )

        self.make_all_mo()

    def post_install(self):
        if Project.opts.enable_gi:
            self.builder.mod_env(
                "INCLUDE", "{}\\include\\cairo".format(self.builder.gtk_dir)
            )
            self.make_single_gir("gtk", prj_dir="gtk3-22")

        self.exec_cmd(
            r"%(gtk_dir)s\bin\glib-compile-schemas.exe %(gtk_dir)s\share\glib-2.0\schemas"
        )
        self.exec_cmd(
            r'%(gtk_dir)s\bin\gtk-update-icon-cache.exe --ignore-theme-index --force "%(gtk_dir)s\share\icons\hicolor"'
        )


@project_add
class Gtk324(Tarball, Meson):
    def __init__(self):
        if self.opts.gtk3_ver != "3.24":
            self.ignore()
            return

        Project.__init__(
            self,
            "gtk3",
            prj_dir="gtk3-24",
            archive_url="http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/3.24/gtk+-3.24.30.tar.xz",
            hash="ba75bfff320ad1f4cfbee92ba813ec336322cc3c660d406aad014b07087a3ba9",
            dependencies=["atk", "gdk-pixbuf", "pango", "libepoxy"],
            patches=[
                "gtk_update_icon_cache.patch",
                "0001-gtk-generate-uac-manifest.py-Fix-UAC-manifest-.rc.patch",
                "0002-gtk-Fix-building-version-resource-on-Windows-11-SDK.patch",
            ],
        )
        if self.opts.enable_gi:
            self.add_dependency("gobject-introspection")
            enable_gi = "true"
        else:
            enable_gi = "false"

        self.add_param("-Dintrospection={}".format(enable_gi))

    def build(self):
        Meson.build(self, meson_params="-Dtests=false -Ddemos=false -Dexamples=false")

        self.install(r".\COPYING share\doc\gtk3")
