#include "ora/c_api.h"
#include "ora/tower.hpp"
#include <cstring>
#include <exception>
#include <string>
static size_t copy_out(const std::string& s,char*out,size_t n){if(out&&n>s.size())std::memcpy(out,s.c_str(),s.size()+1);return s.size();}
extern "C" {
const char* ora_version(void){return "ora.kernel/0.2";}
size_t ora_inspect(const char*t,char*out,size_t n){try{return copy_out(ora::inspect_json(t?t:""),out,n);}catch(...){return copy_out("{\"error\":\"inspection_failed\"}",out,n);}}
size_t ora_scene(uint64_t seed,size_t count,char*out,size_t n){try{return copy_out(ora::stars_json(seed,count),out,n);}catch(...){return copy_out("{\"error\":\"scene_failed\"}",out,n);}}
int ora_compile(const char*s,char*out,size_t n){auto p=ora::Compiler().compile(s?s:"");std::string result=p.valid()?"{\"status\":\"PARSED\",\"grammar\":\"unison.minimal/0.1\",\"effect\":\"NONE\"}":"{\"status\":\"REJECTED\",\"effect\":\"NONE\"}";copy_out(result,out,n);return p.valid()?1:0;}
}
