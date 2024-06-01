import numpy as np
import mido
from mido import MidiFile, MidiTrack, Message

# Define the Mandelbrot function
def mandelbrot(c, max_iter):
    z = c
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

# Define the plot parameters
def mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter):
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width, height))
    for i in range(width):
        for j in range(height):
            n3[i, j] = mandelbrot(r1[i] + 1j*r2[j], max_iter)
    return (r1, r2, n3)

# Map the Mandelbrot set to MIDI notes
def mandelbrot_to_midi(n3, width, height, max_iter):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    tempo = mido.bpm2tempo(120)  # 120 BPM
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    
    # Define MIDI note range
    min_note = 60  # Middle C
    max_note = 84  # Two octaves above middle C
    
    for i in range(width):
        for j in range(height):
            iteration_count = n3[i, j]
            if iteration_count < max_iter:
                note = int(min_note + (iteration_count / max_iter) * (max_note - min_note))
                velocity = 64  # Constant velocity
                duration = 120  # Duration in ticks (quarter note)
                track.append(Message('note_on', note=note, velocity=velocity, time=0))
                track.append(Message('note_off', note=note, velocity=velocity, time=duration))
    
    return mid

# Parameters for Mandelbrot set
xmin, xmax, ymin, ymax = -2.0, 1.0, -1.5, 1.5
width, height, max_iter = 40, 40, 100

r1, r2, n3 = mandelbrot_set(xmin, xmax, ymin, ymax, width, height, max_iter)
mid = mandelbrot_to_midi(n3, width, height, max_iter)

# Save the MIDI file
mid.save('./mandelbrot_music.mid')
