#ifndef eckit_version_h
#define eckit_version_h

#define eckit_VERSION_STR "1.31.5.dev20250909"
#define eckit_VERSION     "1.31.5"

#define eckit_VERSION_MAJOR 1
#define eckit_VERSION_MINOR 31
#define eckit_VERSION_PATCH 5


#ifdef __cplusplus
extern "C" {
#endif

const char * eckit_version();

unsigned int eckit_version_int();

const char * eckit_version_str();

const char * eckit_git_sha1();

#ifdef __cplusplus
}
#endif

#endif // eckit_version_h
