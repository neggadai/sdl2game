#include "Application.hpp"

Application::Application()
{
    SDL_Init(SDL_INIT_VIDEO);
    m_window = SDL_CreateWindow("SDL2 Window",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        1280, 720,
        0);

    if (m_window == nullptr)
    {
        std::cout << "Failed to create window\n";
        std::cout << "SDL2 Error: " << SDL_GetError() << "\n";
        return;
    }

    m_window_surface = SDL_GetWindowSurface(m_window);

    if (m_window_surface == nullptr)
    {
        std::cout << "Failed to get window's surface\n";
        std::cout << "SDL2 Error: " << SDL_GetError() << "\n";
        return;
    }

    m_image = SDL_LoadBMP("c:/profile/downloads/fa99e471c72044cfa48c11ecd9c731a1.bmp");

    if (m_image == nullptr)
    {
        std::cout << "Failed to load image\n";
        std::cout << "SDL2 Error: " << SDL_GetError() << "\n";
        throw 1;
    }
}

Application::~Application()
{
    SDL_FreeSurface(m_window_surface);
    SDL_DestroyWindow(m_window);
}

void Application::update()
{
    bool keep_window_open = true;
    while (keep_window_open)
    {
        m_image_position.x += 1;

        while (SDL_PollEvent(&m_window_event) > 0)
        {
            switch (m_window_event.type)
            {
            case SDL_QUIT:
                keep_window_open = false;
                break;
            }
        }

        draw();
    }
}

void Application::draw()
{
    SDL_BlitSurface(m_image, NULL, m_window_surface, &m_image_position);
    SDL_UpdateWindowSurface(m_window);
}