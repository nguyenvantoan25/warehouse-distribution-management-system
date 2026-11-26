package com.distriflow.shipper.data;

import com.distriflow.shipper.api.ApiClient;
import com.distriflow.shipper.api.ApiException;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/** Server-authoritative state. Unknown POST outcomes retain the exact body and key for explicit retry. */
public final class ShipperRepository {
    private final ApiClient api;
    private JSONObject profile;
    private Pending pending;

    private static final class Pending {
        final String path, body, key;
        Pending(String path, String body) { this.path=path; this.body=body; key=UUID.randomUUID().toString(); }
    }

    public ShipperRepository(String server) { api = new ApiClient(server); }
    public JSONObject profile() { return profile; }
    public boolean hasPending() { return pending != null; }

    public JSONObject login(String username, String password) throws Exception {
        api.clear(); pending = null; profile = null;
        JSONObject body = new JSONObject().put("username", username).put("password", password);
        JSONObject result = object(api.request("POST", "/auth/shipper-login", body.toString(), null));
        if (!"SHIPPER".equals(result.optString("role"))) { api.clear(); throw new ApiException(403, "Chỉ cho phép tài khoản shipper."); }
        api.setCsrf(result.getString("csrfToken"));
        profile = result;
        return result;
    }

    public JSONArray tasks() throws Exception {
        try { return new JSONArray(api.request("GET", "/pickup-tasks", null, null)); }
        catch (JSONException e) { throw new IOException("Máy chủ trả danh sách không hợp lệ."); }
    }

    public JSONObject act(String id, String action, JSONObject body) throws Exception {
        if (pending != null) throw new IllegalStateException("Còn một lệnh chưa rõ kết quả. Hãy thử lại lệnh đó trước.");
        if (!action.matches("respond|arrive|scan|shipper-confirm")) throw new IllegalArgumentException("Thao tác không hợp lệ");
        pending = new Pending("/pickup-tasks/" + URLEncoder.encode(id, StandardCharsets.UTF_8.name()) + "/" + action, body.toString());
        return retry();
    }

    public JSONObject retry() throws Exception {
        if (pending == null) throw new IllegalStateException("Không có lệnh chờ.");
        try {
            JSONObject result = object(api.request("POST", pending.path, pending.body, pending.key));
            pending = null;
            return result;
        } catch (ApiException e) {
            if (e.status < 500) pending = null;
            throw e;
        }
    }

    public void logout() throws Exception {
        try { api.request("POST", "/auth/logout", null, null); }
        finally { clear(); }
    }
    public void clear() { api.clear(); profile=null; pending=null; }

    private JSONObject object(String value) throws IOException {
        try { return new JSONObject(value); }
        catch (JSONException e) { throw new IOException("Chưa xác định kết quả: phản hồi máy chủ không hợp lệ."); }
    }
}
