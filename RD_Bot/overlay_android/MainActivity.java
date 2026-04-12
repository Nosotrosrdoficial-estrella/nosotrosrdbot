package com.rd_bot.overlay;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Toast;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Solicitar permiso de superposición si no está concedido
        if (!Settings.canDrawOverlays(this)) {
            Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION);
            startActivity(intent);
            Toast.makeText(this, "Por favor, concede el permiso de superposición", Toast.LENGTH_LONG).show();
        } else {
            startService(new Intent(this, FloatingService.class));
            Toast.makeText(this, "Servicio flotante iniciado", Toast.LENGTH_SHORT).show();
        }
        finish();
    }
}
