An easy config library.

Types are enforced and can be parsed.

Create a default config:

```
class Config_(ConfigBase):
    version = VersionSetting(0, 1, 0, 'alpha', name='Version', level=Level.USER | Level.READ_ONLY)
    dev_mode = Setting[bool](True, 'Dev Mode', level=Level.USER)
    debug_mode = Setting[bool](True, 'Debug Mode', level=Level.USER_DEV)
    
    class ImageDownloading(ConfigBase):
        convert_image = Setting[bool](True, 'Convert Image')
        preferable_format = Setting[str]('JXL', 'Converted Images Format')
        max_threads = RangeSetting[int](1, multiprocessing.cpu_count(), 1, multiprocessing.cpu_count(), 'Max Download Threads')
        
    class Dirs(StdDirConfigBase):
        STD_DIR = StdDirConfigBase.STD_DIR
        
        IMG = 'images'
        LOL = 'lol/kek/s.json'
        
        class CACHE(DirConfigBase):
            JSON = 'cache.json'
            
    class Enums(EnumsConfig):
        class Foo(En):
            BAR = a()
            BAR2 = a()

Config = Config_()
```

Save and load Config.

Access any Setting's value with Config.ImageDownload.convert_image()

Specify Setting's units, name, description, level and type.
Set value boundaries.
Add dependency Settings.
Set activity and visibility of Setting based on their dependencies.