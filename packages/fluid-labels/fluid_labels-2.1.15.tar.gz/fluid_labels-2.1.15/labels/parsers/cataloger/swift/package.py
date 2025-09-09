from packageurl import PackageURL
from pydantic import BaseModel, ConfigDict, ValidationError

from labels.model.file import Location
from labels.model.indexables import ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.utils import log_malformed_package_warning


class SwiftPackageManagerResolvedEntry(BaseModel):
    revision: str
    model_config = ConfigDict(frozen=True)


class CocoaPodfileLockEntry(BaseModel):
    checksum: str
    model_config = ConfigDict(frozen=True)


def extract_package_name(url: str) -> str:
    return url.split("://", 1)[-1].replace('"', "").removesuffix(".git")


def is_stable_package_version(version: str) -> bool:
    unstable_identifiers = (
        "alpha",
        "beta",
        "rc",
        "next",
        "preview",
        "pre",
        "dev",
        "snapshot",
        "canary",
        "nightly",
    )

    return not any(identifier in version for identifier in unstable_identifiers)


def new_cocoa_pods_package(
    name: str,
    version: str,
    hash_: ParsedValue,
    location: Location,
) -> Package | None:
    if not isinstance(hash_, str):
        return None
    try:
        return Package(
            name=name,
            version=version,
            p_url=PackageURL(type="cocoapods", name=name, version=version).to_string(),  # type: ignore[misc]
            locations=[location],
            type=PackageType.CocoapodsPkg,
            language=Language.SWIFT,
            metadata=CocoaPodfileLockEntry(checksum=hash_),
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(location, ex)
        return None


def new_swift_package_manager_package(
    *,
    source_url: str,
    version: str,
    revision: ParsedValue | None,
    location: Location,
) -> Package | None:
    name = extract_package_name(source_url)

    try:
        return Package(
            name=name,
            version=version,
            p_url=PackageURL(type="swift", name=name, version=version).to_string(),  # type: ignore[misc]
            locations=[location],
            type=PackageType.SwiftPkg,
            language=Language.SWIFT,
            metadata=SwiftPackageManagerResolvedEntry(revision=revision)
            if revision and isinstance(revision, str)
            else None,
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(location, ex)
        return None
