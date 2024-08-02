
#pragma warning(push,3)
#include <SDL2/SDL.h>
#include <SDL2/SDL2_gfxPrimitives.h>
#include <iostream>
#pragma warning(pop)

#include "Application.hpp"

int main(int , char* [])
{
    Application app;
    app.loop(); 

	return 0;
}

