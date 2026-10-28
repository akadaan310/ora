#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace ora {
enum class Tower : uint8_t { Observation, Letter, Form, Grammar, Operator,
  Compiler, Machine, Generator, Oracle, Orb, Ora, Sovereign };
inline constexpr const char* tower_name(Tower t) {
  constexpr const char* names[]{"observation","letter","form","grammar","operator","compiler",
    "machine","generator","oracle","orb","ora","sovereign"};
  return names[static_cast<size_t>(t)];
}
struct Symbol { std::string id, lexeme, alphabet_id; };
struct Alphabet {
  std::string id, version;
  std::vector<Symbol> members;
  bool contains(std::string_view s) const {
    return std::any_of(members.begin(), members.end(), [&](const Symbol& sym){ return sym.lexeme == s; });
  }
};
struct Form { std::string id, input_type, output_type; std::map<std::string,std::string> features; };
struct Production { std::string lhs; std::vector<std::string> rhs; std::string result_type; };
struct Grammar { std::string id; std::vector<Production> rules; };
enum class Effect { Pure, Observe, LocalWrite, Network, Privileged };
struct Operator { std::string id,input_type,output_type; Effect effect=Effect::Pure; bool admitted=false; };
struct Ast { std::string kind, type, value; std::vector<Ast> children; };
struct Program { std::string grammar, source; Ast ast; std::vector<std::string> errors; bool valid()const{return errors.empty();} };
struct Mission { std::string id, goal, success_predicate; unsigned attempt_budget=3; std::set<std::string> permitted_effects; };
struct Oracle { std::string id, domain, version; std::set<std::string> operator_ids; };
struct Orb {std::string id,version;std::set<std::string> capabilities;};
struct Aura {std::string id, parent_id;std::set<std::string> grants;std::map<std::string,std::string> state;};
class Compiler {
public:
  // Small, honest grammar. Syntax: OBSERVE <subject> | GENERATE <recipe> | ANALYZE <text>.
  // Arbitrary natural language is out of scope, never fabricated.
  Program compile(const std::string &source) const;
};
struct Transition {std::string region,from,event,to;};
class Machine {
  std::vector<Transition> edges_;
public:
  void add(Transition x){edges_.push_back(std::move(x));}
  // Proposed simultaneous changes read the *same* source snapshot, rejecting conflicting writes.
  bool step(Aura &a,const std::string &event)const;
};
class Registry {
  std::map<std::string,Operator> operators_;
public:
  void propose(Operator o);
  void admit(const std::string &id,bool independently_tested,bool authorized_reviewer);
  bool may_invoke(const Aura &a,const std::string &id)const;
};
struct Star { uint32_t index;double u,v,phase,frequency,amplitude; };
std::vector<Star> starfield(uint64_t seed,size_t count);
double brightness(const Star& star,uint64_t tick,uint32_t hz=24);
std::string stars_json(uint64_t seed,size_t count);
std::string inspect_json(const std::string &text);
} // namespace ora

