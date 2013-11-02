include "damn_types.thrift"

typedef string Mimetype


exception AnalyzerException {
  1: string msg
}

service DamnService {
    void ping(),
    
    list<Mimetype> get_supported_mimetypes(),
    
    map<Mimetype, damn_types.TargetMimetype> get_target_mimetypes(),
    
    damn_types.FileReference analyze(1:damn_types.File file) throws (1:AnalyzerException ae)
}
