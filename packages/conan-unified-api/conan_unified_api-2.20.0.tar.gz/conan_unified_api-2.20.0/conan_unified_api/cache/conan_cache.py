import json
from multiprocessing import RLock
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from conan_unified_api.base import conan_version
from conan_unified_api.base.helper import delete_path
from conan_unified_api.base.logger import Logger
from conan_unified_api.common import ConanUnifiedApi
from conan_unified_api.types import ConanRef


class ConanInfoCache:
    """
    This is a cache to accelerate calls which need remote access.
    It also has an option to store the local package path.
    """

    CACHE_FILE_NAME = "cache.json"
    if conan_version.major == 2:
        CACHE_FILE_NAME = "cacheV2.json"

    def __init__(self, cache_dir: Path, local_refs: Optional[List[ConanRef]] = None):
        if not local_refs:
            local_refs = []

        self._cache_file = cache_dir / self.CACHE_FILE_NAME
        self._remote_packages: Dict[str, Dict[str, List[str]]] = {}
        self._read_only = False  # for testing purposes
        self._access_lock = RLock()

        # create cache file, if it does not exist
        if not self._cache_file.exists():
            self._cache_file.touch()
            return

        # read cached info
        self._load()

    def get_similar_remote_pkg_refs(self, name: str, user: str) -> List[ConanRef]:
        """
        Return cached info on remotely available conan refs from the same ref name and user.
        """
        if not user:  # official pkgs have no user, substituted by _
            user = "_"
        refs: List[ConanRef] = []
        with self._access_lock:
            if user == "*":  # find all refs with same name
                name_pkgs = self._remote_packages.get(name, {})
                for user in name_pkgs:
                    for version_channel in self._remote_packages.get(name, {}).get(user, []):
                        version, channel = version_channel.split("/")
                        refs.append(ConanRef(name, version, user, channel))
            else:
                user_pkgs = self._remote_packages.get(name, {}).get(user, [])
                for version_channel in user_pkgs:
                    version, channel = version_channel.split("/")
                    refs.append(ConanRef(name, version, user, channel))
        return refs

    def get_all_remote_refs(self) -> List[str]:
        """Return all remote references. Updating, when queries finish."""
        refs = []
        with self._access_lock:
            for name in self._remote_packages:
                for user in self._remote_packages[name]:
                    for version_channel in self._remote_packages.get(name, {}).get(user, []):
                        version, channel = version_channel.split("/")
                        refs.append(str(ConanRef(name, version, user, channel)))
        return refs

    def search(self, query: str) -> Set[str]:
        """
        Return cached info on available conan refs from a query
        """
        with self._access_lock:
            remote_refs = set()
            # try to extract name and user from query
            split_query = query.split("/")
            name = split_query[0]
            user = "*"
            if len(split_query) > 1:
                user_split = split_query[1].split("@")
                if len(user_split) > 1:
                    user = user_split[1]
            for ref in self.get_similar_remote_pkg_refs(name, user):
                remote_refs.add(str(ref))
            return remote_refs

    def invalidate_remote_package(self, conan_ref: Union[ConanRef, str]) -> None:
        """Remove a package, wich was removed on the remote"""
        conan_ref = ConanUnifiedApi.conan_ref_from_reflike(conan_ref)
        version_channels = self._remote_packages.get(conan_ref.name, {}).get(
            str(conan_ref.user), []
        )
        invalid_version_channel = f"{conan_ref.version}/{conan_ref.channel}"
        if invalid_version_channel in version_channels:
            Logger().debug(f"Invalidated {conan_ref!s} from remote cache.")
            version_channels.remove(f"{conan_ref.version}/{conan_ref.channel}")
            self._save()

    def update_remote_package_list(
        self, remote_packages: List[ConanRef], invalidate: bool = False
    ) -> None:
        """
        Update the cache with the info of several remote packages.
        Invalidate option clears the cache.
        """
        with self._access_lock:
            if invalidate:  # clear cache
                self._remote_packages.clear()
                self._save()
            for ref in remote_packages:
                # convert back the official cache entries
                user = str(ref.user)
                channel = ref.channel
                if ref.user is None and ref.channel is None:
                    user = "_"
                    channel = "_"
                current_version_channel = f"{ref.version}/{channel}"
                version_channels = set(self._remote_packages.get(ref.name, {}).get(user, []))
                if current_version_channel not in version_channels:
                    version_channels.add(current_version_channel)
                    version_channels_list = list(version_channels)
                    if not self._remote_packages.get(ref.name):
                        self._remote_packages.update({ref.name: {}})
                    self._remote_packages.get(ref.name, {}).update(
                        {user: version_channels_list}
                    )

            self._save()

    def _load(self) -> None:
        """Load the cache."""
        json_data = {}
        try:
            with open(self._cache_file) as json_file:
                content = json_file.read()
                if len(content) > 0:
                    json_data = json.loads(content)
        except Exception:  # possibly corrupt, delete cache file
            Logger().debug("ConanCache: Can't read speedup-cache file, deleting it.")
            delete_path(self._cache_file)
            # create file anew
            self._cache_file.touch()
            return
        self._remote_packages = json_data.get("remote_packages", {})
        self._read_only = json_data.get("read_only", False)

    def _save(self) -> None:
        """Write the cache to file."""
        if self._read_only:
            return
        json_data = {}
        with self._access_lock:
            json_data["read_only"] = self._read_only
            json_data["remote_packages"] = self._remote_packages
            try:
                with open(self._cache_file, "w") as json_file:
                    json.dump(json_data, json_file)
            except Exception:
                Logger().debug("ConanCache: Can't save speedup-cache file.")
