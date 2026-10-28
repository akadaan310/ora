#include "ora/tower.hpp"
#include <cctype>
#include <iomanip>
#include <utility>

namespace ora {
[[maybe_unused]] static std::string escape(const std::string&s){std::ostringstream o;for(unsigned char x:s){if(x=='"'||x=='\\')o<<'\\'<<char(x);else if(x=='\n')o<<"\\n";else if(x=='\r')o<<"\\r";else if(x=='\t')o<<"\\t";else if(x<32)o<<"\\u00"<<std::hex<<std::setw(2)<<std::setfill('0')<<(int)x<<std::dec;else o<<char(x);}return o.str();}
static uint64_t rand64(uint64_t& x){uint64_t z=(x+=0x9E3779B97F4A7C15ULL);z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL;z=(z^(z>>27))*0x94D049BB133111EBULL;return z^(z>>31);}
static double unit(uint64_t& x){return (rand64(x)>>11)*0x1.0p-53;}
Program Compiler::compile(const std::string&source)const{
  Program p{"unison.minimal/0.1",source,{"PROGRAM","program","",{}},{}};
  if(source.size()>1024){p.errors.push_back("source_too_long");return p;}
  std::istringstream in(source);std::string verb,subject;
  in>>verb;std::getline(in,subject);
  for(auto &c:verb)c=char(std::toupper((unsigned char)c));
  const std::map<std::string,std::string> allowed={{"OBSERVE","observation"},{"ANALYZE","analysis"},{"GENERATE","proposal"}};
  auto it=allowed.find(verb);
  if(it==allowed.end()){p.errors.push_back("unknown_operator");return p;}
  auto begin=subject.find_first_not_of(" \t\r\n");
  if(begin==std::string::npos){p.errors.push_back("empty_operand");return p;}
  subject=subject.substr(begin);
  p.ast.children.push_back({verb,it->second,subject,{}});
  return p;
}
bool Machine::step(Aura &a,const std::string&event)const{
  auto next=a.state;std::set<std::string> written;bool changed=false;
  for(const auto&e:edges_){
    const auto it=a.state.find(e.region);
    if(e.event!=event||it==a.state.end()||it->second!=e.from)continue;
    if(!written.insert(e.region).second)return false; // conflict: original remains untouched
    next[e.region]=e.to;changed=true;
  }
  if(changed)a.state=std::move(next);
  return changed;
}
void Registry::propose(Operator o){if(o.id.empty()||operators_.count(o.id))throw std::invalid_argument("duplicate or empty operator");o.admitted=false;operators_.emplace(o.id,std::move(o));}
void Registry::admit(const std::string&id,bool tested,bool reviewer){auto i=operators_.find(id);if(i==operators_.end()||!tested||!reviewer)throw std::logic_error("admission requires independent test and reviewer");i->second.admitted=true;}
bool Registry::may_invoke(const Aura &a,const std::string &id)const{auto i=operators_.find(id);return i!=operators_.end()&&i->second.admitted&&a.grants.count(id)!=0;}
std::vector<Star> starfield(uint64_t seed,size_t count){if(count>100000)throw std::invalid_argument("star budget");std::vector<Star> out;out.reserve(count);for(size_t i=0;i<count;i++){out.push_back({uint32_t(i),unit(seed),unit(seed),unit(seed)*6.283185307179586,0.2+unit(seed)*2.7,0.1+unit(seed)*0.8});}return out;}
double brightness(const Star &star,uint64_t tick,uint32_t hz){if(hz==0)throw std::invalid_argument("clock rate");const double phase=6.283185307179586*star.frequency*(double(tick)/hz)+star.phase;auto v=.5+.5*std::sin(phase);return std::clamp(.16+star.amplitude*v*v*v,0.0,1.0);}
std::string stars_json(uint64_t seed,size_t count){auto data=starfield(seed,count);std::ostringstream o;o<<"{\"grammar\":\"surface.stars/0.1\",\"seed\":"<<seed<<",\"stars\":[";o<<std::setprecision(17);for(size_t i=0;i<data.size();i++){auto&s=data[i];if(i)o<<',';o<<"{\"id\":"<<s.index<<",\"u\":"<<s.u<<",\"v\":"<<s.v<<",\"phase\":"<<s.phase<<",\"frequency\":"<<s.frequency<<",\"amplitude\":"<<s.amplitude<<"}";}return o.str()+"]}";}
std::string inspect_json(const std::string&text){if(text.size()>1000000)throw std::invalid_argument("text budget");size_t codepoints=0,words=0;bool inword=false;for(size_t i=0;i<text.size();i++){unsigned char c=text[i];if((c&0xC0)!=0x80)++codepoints;if(c<=32){inword=false;}else if(!inword){++words;inword=true;}}std::ostringstream o;o<<"{\"grammar\":\"language.utf8-inspect/0.1\",\"codepoints\":"<<codepoints<<",\"bytes\":"<<text.size()<<",\"whitespace_tokens\":"<<words<<",\"status\":\"FORMAL_INSPECTION_ONLY\"}";return o.str();}
}

