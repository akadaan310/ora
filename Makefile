CXX ?= g++
FLAGS = -std=c++20 -O2 -Wall -Wextra -Werror -fPIC -Iinclude
all: build/libora.so test
build:
	mkdir -p build
build/libora.so: include/ora/tower.hpp include/ora/c_api.h src/tower.cpp src/c_api.cpp | build
	$(CXX) $(FLAGS) -shared src/tower.cpp src/c_api.cpp -o $@
test: build/libora.so tests/tower_test.cpp
	$(CXX) $(FLAGS) tests/tower_test.cpp -Lbuild -lora -Wl,-rpath,'$$ORIGIN' -o build/tower-test
	./build/tower-test
clean:
	rm -rf build
.PHONY: test clean all

