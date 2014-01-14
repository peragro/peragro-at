enum MetaDataType {
  BOOL = 1,
  INT = 2,
  DOUBLE = 3,
  STRING = 4
}

struct MetaDataValue {
  1: MetaDataType type,
  2: optional bool bool_value,
  3: optional i64 int_value,
  4: optional double double_value,
  5: optional string string_value,
}

struct TargetMimetypeOption {
  1: string name,
  2: string description,
  3: string type,
  4: string constraint,
  5: string default_value,
}

struct TargetMimetype {
  1: string mimetype,
  2: string description,
  3: string template,
  4: list<TargetMimetypeOption> options = [],
}

struct File {
    1:string filename,
    2:binary data
}

struct FileId {
    1:string filename,
    2:optional string hash,
}

struct AssetId {
    1:string subname,
    2:string mimetype,
    3:FileId file,
}

struct AssetReference {
    1:AssetId asset,
    2:map<string,MetaDataValue> metadata,
    3:list<AssetId> dependencies
}
 
struct FileReference {
    1:FileId file,
    2:string mimetype,
    3:map<string,MetaDataValue> metadata,
    4:list<AssetReference> assets
}
