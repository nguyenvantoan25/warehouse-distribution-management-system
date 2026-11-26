package com.distriflow.shipper.config;

import java.net.URI;
import java.util.Locale;

/** No credentials/query parameters in server URLs. HTTP is debug/private-network only. */
public final class ServerAddress {
    private ServerAddress() {}

    public static String normalize(String value, boolean debug) {
        try {
            URI uri = new URI(value.trim());
            String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(Locale.ROOT);
            String host = uri.getHost();
            if (host == null || uri.getRawUserInfo() != null || uri.getRawQuery() != null || uri.getRawFragment() != null
                    || uri.getPort() == 0 || uri.getPort() > 65535) throw new IllegalArgumentException();
            if (!scheme.equals("https") && !(scheme.equals("http") && debug && isPrivateHost(host))) {
                throw new IllegalArgumentException("Cần HTTPS. Bản test chỉ cho HTTP trên localhost hoặc IP nội bộ.");
            }
            String path = uri.getPath();
            if (!(path.isEmpty() || path.equals("/") || path.equals("/api/v1") || path.equals("/api/v1/"))) {
                throw new IllegalArgumentException();
            }
            return new URI(scheme, null, host.toLowerCase(Locale.ROOT), uri.getPort(), null, null, null).toASCIIString();
        } catch (Exception e) {
            throw new IllegalArgumentException("Địa chỉ máy chủ không hợp lệ. Dùng HTTPS; bản test cho phép HTTP với IP nội bộ.");
        }
    }

    public static boolean isPrivateHost(String host) {
        if (host.equalsIgnoreCase("localhost") || host.equals("::1") || host.equals("[::1]")) return true;
        String[] parts = host.split("\\.");
        if (parts.length != 4) return false;
        int[] numbers = new int[4];
        try {
            for (int i = 0; i < 4; i++) {
                if (!parts[i].matches("[0-9]{1,3}")) return false;
                if (parts[i].length() > 1 && parts[i].charAt(0) == '0') return false;
                numbers[i] = Integer.parseInt(parts[i]);
                if (numbers[i] > 255) return false;
            }
        } catch (NumberFormatException e) { return false; }
        return numbers[0] == 10 || numbers[0] == 127
                || (numbers[0] == 192 && numbers[1] == 168)
                || (numbers[0] == 172 && numbers[1] >= 16 && numbers[1] <= 31);
    }
}
