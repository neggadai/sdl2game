#pragma once
#pragma warning(push,3)
#include <SDL2/SDL.h>
#pragma warning(pop)

#pragma warning(push,3)
#include <iostream>
#pragma warning(pop)

#include "Character.hpp"

class Application
{
public:
	Application();
	~Application();

	void loop();
	void update(double delta_time);
	void draw();

private:
	StickFigure m_stick_figure;
	Application(const Application&) = delete;
	Application& operator=(const Application&) = delete;

	SDL_Window *m_window = nullptr;
	SDL_Surface* m_window_surface = nullptr;
	SDL_Event m_window_event = {};
};

