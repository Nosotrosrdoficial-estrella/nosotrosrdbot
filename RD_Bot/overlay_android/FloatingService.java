package com.rd_bot.overlay;

import android.app.Service;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.net.LocalServerSocket;
import android.net.LocalSocket;
import android.os.IBinder;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.WindowManager;
import android.widget.Toast;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class FloatingService extends Service {
    private WindowManager windowManager;
    private View floatingView;
    private Thread socketThread;
    private boolean running = true;

    @Override
    public IBinder onBind(Intent intent) { return null; }

    @Override
    public void onCreate() {
        super.onCreate();
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        LayoutInflater inflater = (LayoutInflater) getSystemService(LAYOUT_INFLATER_SERVICE);
        floatingView = inflater.inflate(R.layout.floating_layout, null);
        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);
        params.gravity = Gravity.TOP | Gravity.LEFT;
        params.x = 0;
        params.y = 100;
        windowManager.addView(floatingView, params);
        startSocketServer();
    }

    private void startSocketServer() {
        socketThread = new Thread(() -> {
            try {
                java.net.ServerSocket serverSocket = new java.net.ServerSocket(8080);
                while (running) {
                    java.net.Socket client = serverSocket.accept();
                    BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                    String line;
                    while ((line = in.readLine()) != null) {
                        if (line.equals("FOUND")) {
                            showToast("Texto RD$ detectado!");
                        }
                    }
                    client.close();
                }
                serverSocket.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
        socketThread.start();
    }

    private void showToast(String msg) {
        new android.os.Handler(getMainLooper()).post(() ->
            Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_SHORT).show()
        );
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        running = false;
        if (floatingView != null) windowManager.removeView(floatingView);
    }
}
