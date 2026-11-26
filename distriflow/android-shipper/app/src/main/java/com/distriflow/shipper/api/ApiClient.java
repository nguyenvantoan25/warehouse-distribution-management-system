package com.distriflow.shipper.api;

import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.CookieManager;
import java.net.CookiePolicy;
import java.net.HttpURLConnection;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.List;
import java.util.Map;

/** Native HTTP, isolated in-memory cookie jar, default TLS validation. Never logs requests/secrets. */
public final class ApiClient {
    private final String base;
    private final CookieManager cookies = new CookieManager(null, CookiePolicy.ACCEPT_ORIGINAL_SERVER);
    private String csrf = "";

    public ApiClient(String server) { base = server + "/api/v1"; }
    public void setCsrf(String value) { csrf = value; }
    public void clear() { cookies.getCookieStore().removeAll(); csrf = ""; }

    public String request(String method, String path, String body, String key) throws IOException, ApiException {
        URI uri = URI.create(base + path);
        HttpURLConnection connection = (HttpURLConnection) uri.toURL().openConnection();
        try {
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(20000);
            connection.setInstanceFollowRedirects(false);
            connection.setRequestMethod(method);
            connection.setRequestProperty("Accept", "application/json");
            if (!csrf.isEmpty()) connection.setRequestProperty("X-CSRF-Token", csrf);
            if (key != null) connection.setRequestProperty("Idempotency-Key", key);
            for (Map.Entry<String,List<String>> header : cookies.get(uri, Collections.emptyMap()).entrySet()) {
                for (String value : header.getValue()) connection.addRequestProperty(header.getKey(), value);
            }
            if (body != null) {
                byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                connection.setDoOutput(true);
                connection.setFixedLengthStreamingMode(bytes.length);
                try (java.io.OutputStream out = connection.getOutputStream()) { out.write(bytes); }
            }
            int status = connection.getResponseCode();
            cookies.put(uri, connection.getHeaderFields());
            String response = read(status >= 400 ? connection.getErrorStream() : connection.getInputStream());
            if (status < 200 || status >= 300) {
                String message = "Yêu cầu không thành công (HTTP " + status + ").";
                try {
                    JSONObject error = new JSONObject(response).optJSONObject("error");
                    if (error != null) message = error.optString("message", message);
                } catch (Exception ignored) { /* Never display arbitrary HTML or raw server data. */ }
                throw new ApiException(status, message);
            }
            return response;
        } finally { connection.disconnect(); }
    }

    private String read(InputStream input) throws IOException {
        if (input == null) return "";
        try (InputStream in = input; ByteArrayOutputStream bytes = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192];
            int count;
            while ((count = in.read(buffer)) != -1) {
                if (bytes.size() + count > 2 * 1024 * 1024) throw new IOException("Phản hồi quá lớn; cần phân trang phía máy chủ.");
                bytes.write(buffer, 0, count);
            }
            return bytes.toString(StandardCharsets.UTF_8.name());
        }
    }
}
