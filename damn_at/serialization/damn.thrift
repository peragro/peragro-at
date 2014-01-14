include "damn_types.thrift"

typedef string Mimetype


exception AnalyzerException {
  1: string msg
}

exception TranscoderException {
  1: string msg
}

service DamnService {
    void ping(),
    
    list<Mimetype> get_supported_mimetypes(),
    
    map<Mimetype, list<damn_types.TargetMimetype>> get_target_mimetypes(),
    
    damn_types.FileReference analyze(1:damn_types.File file) throws (1:AnalyzerException ae),
    
    list<damn_types.File> transcode(1:list<damn_types.File> files, 2:damn_types.AssetId asset, 3:Mimetype mimetype, 4:map<string, string> options) throws (1:TranscoderException te)
}
