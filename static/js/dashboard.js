/*
Created by Tooba Jatoi
Copyright © 2025 Tooba Jatoi. All rights reserved.
*/

document.addEventListener("DOMContentLoaded", () => {
  const meter = document.getElementById('meter');
  const meterFill = document.getElementById('meterFill');
  const statusText = document.getElementById('statusText');
  const socket = io();

  // Initialize status
  statusText.textContent = 'Connected to server';

  socket.on('connect', () => {
    statusText.textContent = 'Listening for audio...';
  });

  socket.on('disconnect', () => {
    statusText.textContent = 'Disconnected from server';
  });

  socket.on('mood_update', data => {
    const score = parseFloat(data.score);
    const pct = score.toFixed(1);
    
    // Update meter text
    meter.textContent = `${pct}%`;
    
    // Update progress bar
    meterFill.style.width = `${score}%`;
    
    // Update status
    statusText.textContent = 'Processing audio...';
    
    // Add visual feedback based on emotional intensity
    let color;
    if (score < 30) {
      color = '#48bb78';  // Green for low intensity
      statusText.textContent = 'Low emotional intensity detected';
    } else if (score < 70) {
      color = '#ed8936';  // Orange for medium intensity
      statusText.textContent = 'Medium emotional intensity detected';
    } else {
      color = '#f56565';  // Red for high intensity
      statusText.textContent = 'High emotional intensity detected';
    }
    
    // Animate the meter fill
    meterFill.style.background = `linear-gradient(90deg, ${color} 0%, ${color}dd 100%)`;
    
    // Reset status after 3 seconds
    setTimeout(() => {
      statusText.textContent = 'Listening for audio...';
    }, 3000);
  });

  socket.on('error', (data) => {
    statusText.textContent = `Error: ${data.message}`;
    setTimeout(() => {
      statusText.textContent = 'Listening for audio...';
    }, 5000);
  });
}); 