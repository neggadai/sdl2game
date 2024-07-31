#pragma once

#include "Character.hpp"
#include <SDL2/SDL.h>
#include <iostream>

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

	SDL_Surface* m_image = nullptr;
	SDL_Rect m_image_position = {};

	double m_image_x = 0.0;
	double m_image_y = 0.0;

};

