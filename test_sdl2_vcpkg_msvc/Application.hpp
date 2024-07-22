#pragma once

#include <SDL2/SDL.h>
#include <iostream>

class Application
{
public:
	Application();
	~Application();

	void update();
	void draw();

private:
	SDL_Window* m_window = nullptr;
	SDL_Surface* m_window_surface = nullptr;
	SDL_Event m_window_event = {};

	SDL_Surface* m_image = nullptr;
	SDL_Rect     m_image_position = {};
};