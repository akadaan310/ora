#include "ora/tower.hpp"
#include "ora/c_api.h"
#include <cassert>
#include <cstring>
#include <iostream>
int main(){using namespace ora;
  static_assert(static_cast<unsigned>(Tower::Sovereign)==11);
  Alphabet arabic{"qitt.abjad","0.1",{{"alif","ا","qitt.abjad"},{"ba","ب","qitt.abjad"}}};assert(arabic.contains("ا")&&!arabic.contains("x"));
  auto compiled=Compiler().compile("OBSERVE sky");assert(compiled.valid()&&compiled.ast.children.front().type=="observation");assert(!Compiler().compile("EXECUTE shell").valid());assert(!Compiler().compile("BUILD").valid());
  Aura a{"ora-test","",{"sky.observe"},{{"lifecycle","READY"},{"observing","IDLE"}}};
  Machine sm;sm.add({"lifecycle","READY","ACTIVATE","RUNNING"});sm.add({"observing","IDLE","ACTIVATE","AWAKE"});assert(sm.step(a,"ACTIVATE"));assert(a.state.at("lifecycle")=="RUNNING"&&a.state.at("observing")=="AWAKE");
  Machine conflict;conflict.add({"observing","AWAKE","T","X"});conflict.add({"observing","AWAKE","T","Y"});assert(!conflict.step(a,"T"));assert(a.state.at("observing")=="AWAKE");
  Registry r;r.propose({"sky.observe","subject","analysis",Effect::Observe,false});assert(!r.may_invoke(a,"sky.observe"));bool blocked=false;try{r.admit("sky.observe",false,true);}catch(...){blocked=true;}assert(blocked);r.admit("sky.observe",true,true);assert(r.may_invoke(a,"sky.observe"));
  auto s1=stars_json(1234,210);auto s2=stars_json(1234,210);auto s3=stars_json(1235,210);assert(s1==s2&&s1!=s3);auto points=starfield(1234,210);assert(points.size()==210&&brightness(points.front(),24)>=0&&brightness(points.front(),24)<=1);
  auto details=inspect_json("hello العالم");assert(details.find("codepoints")!=std::string::npos);assert(std::strlen(ora_version())>0);
  char buf[1000];auto need=ora_inspect("hello",nullptr,0);assert(need<sizeof(buf));assert(ora_inspect("hello",buf,sizeof(buf))==need);assert(ora_compile("ANALYZE text",buf,sizeof(buf))==1);assert(ora_compile("RUN rm -rf",buf,sizeof(buf))==0);
  std::cout<<"PASS C++: 12 tower levels, Unicode registry, AST, simultaneous FSM, conflict, capability admission, deterministic scene, C ABI\n";
}
