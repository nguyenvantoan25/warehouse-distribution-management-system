package com.distriflow.shipper.ui;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.view.WindowInsets;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import com.distriflow.shipper.BuildConfig;
import com.distriflow.shipper.api.ApiException;
import com.distriflow.shipper.config.ServerAddress;
import com.distriflow.shipper.data.ShipperRepository;
import com.distriflow.shipper.data.TaskRules;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Consumer;

/** Native Android UI. Credentials/session/pending commands never enter persistent storage. */
public final class MainActivity extends Activity {
    private static final int INK=0xff0f172a, MUTED=0xff64748b, ORANGE=0xffea580c, BG=0xfff8fafc;
    private final ExecutorService network = Executors.newSingleThreadExecutor();
    private final List<JSONObject> tasks = new ArrayList<>();
    private ShipperRepository repository;
    private LinearLayout root, content;
    private boolean busy;
    private String tab="Nhiệm vụ", activeId="", message="", username="", server="";

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        server = getPreferences(MODE_PRIVATE).getString("server", BuildConfig.DEBUG ? "http://127.0.0.1:8000" : "");
        if (Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(false);
        render();
    }

    private boolean loggedIn() { return repository != null && repository.profile() != null; }
    private int dp(float value) { return (int)(getResources().getDisplayMetrics().density*value+0.5f); }

    private void render() {
        root = new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(BG);
        root.setOnApplyWindowInsetsListener((v,insets)-> {
            v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());
            return insets;
        });
        setContentView(root); root.requestApplyInsets();
        LinearLayout header = new LinearLayout(this); header.setPadding(dp(20),dp(14),dp(20),dp(14)); header.setBackgroundColor(Color.WHITE);
        TextView brand = text("DistriFlow  /  SHIPPER",18,INK,true); header.addView(brand); root.addView(header);
        ScrollView scroll = new ScrollView(this); scroll.setFillViewport(true);
        content = new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL); content.setPadding(dp(20),dp(20),dp(20),dp(28));
        scroll.addView(content); root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        if (busy) { ProgressBar spinner = new ProgressBar(this); content.addView(spinner,new LinearLayout.LayoutParams(dp(32),dp(32))); }
        if (!message.isEmpty()) note(message);
        if (!loggedIn()) { loginForm(); return; }
        title(tab); label("Xin chào, " + repository.profile().optString("username"));
        if (repository.hasPending()) {
            note("Một lệnh chưa rõ kết quả. Không xác nhận lại bằng lệnh mới; thử lại cùng mã lệnh hoặc tải dữ liệu để kiểm tra.");
            button("Thử lại lệnh chưa rõ kết quả",()->request(repository::retry,this::acceptTask),true);
        }
        if (tab.equals("Tài khoản")) account();
        else if (tab.equals("Lịch sử")) taskList(true);
        else {
            button("Tải lại từ máy chủ",this::loadTasks,true);
            JSONObject task=active();
            if (task==null) taskList(false); else taskDetail(task);
        }
        navigation();
    }

    private void loginForm() {
        title("Đăng nhập shipper"); label("Dùng tài khoản được phân công trên hệ thống DistriFlow.");
        if (BuildConfig.DEBUG) note("Bản test: có thể dùng HTTP trên mạng nội bộ. Điện thoại qua USB cần adb reverse cổng 8000.");
        EditText address=input("Máy chủ API",server,InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_URI);
        address.setHint("https://api.ten-mien-cua-ban"); address.setId(View.generateViewId());
        EditText user=input("Tên đăng nhập",username,InputType.TYPE_CLASS_TEXT);
        EditText password=input("Mật khẩu","",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
        password.setSaveEnabled(false); password.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO);
        Button login=button("Đăng nhập",()-> {
            final String secret=password.getText().toString();
            username=user.getText().toString().trim();
            try { server=ServerAddress.normalize(address.getText().toString(),BuildConfig.DEBUG); }
            catch (IllegalArgumentException e) { message=e.getMessage(); render(); return; }
            if (username.isEmpty() || secret.isEmpty()) { message="Nhập tên đăng nhập và mật khẩu."; render(); return; }
            password.setText(""); getPreferences(MODE_PRIVATE).edit().putString("server",server).apply();
            repository=new ShipperRepository(server);
            request(()->repository.login(username,secret),profile->{ message=""; tab="Nhiệm vụ"; activeId=""; loadTasks(); });
        },true);
        password.setImeOptions(EditorInfo.IME_ACTION_DONE);
        password.setOnEditorActionListener((v,action,event)->{if(action==EditorInfo.IME_ACTION_DONE){login.performClick();return true;}return false;});
        label("Không lưu mật khẩu trên thiết bị. Phiên đăng nhập chỉ nằm trong bộ nhớ và phải đăng nhập lại sau khi ứng dụng bị đóng.");
    }

    private void loadTasks() {
        request(repository::tasks,array->{
            tasks.clear(); for(int i=0;i<array.length();i++){JSONObject t=array.optJSONObject(i);if(t!=null)tasks.add(t);}
            if(active()==null) activeId="";
            message=repository.hasPending()?"Đã tải dữ liệu. Lệnh chưa rõ kết quả vẫn giữ nguyên để thử lại an toàn.":"Đã tải dữ liệu từ máy chủ.";
        });
    }

    private JSONObject active() { for(JSONObject t:tasks)if(t.optString("id").equals(activeId))return t;return null; }

    private void taskList(boolean history) {
        int count=0;
        for(JSONObject task:tasks) {
            boolean complete=task.optString("status").equals("handed_over"); if(complete!=history)continue; count++;
            LinearLayout card=card(); card.addView(text(task.optString("code"),17,INK,true));
            card.addView(text(task.optString("warehouseName"),15,MUTED,false));
            card.addView(text(status(task.optString("status"))+" · "+strings(task.optJSONArray("packages")).size()+" kiện",14,MUTED,false));
            Button open=makeButton("Mở "+task.optString("code"),()->{activeId=task.optString("id");tab="Nhiệm vụ";message="";render();},true);
            card.addView(open);
        }
        if(count==0) note(history?"Chưa có nhiệm vụ bàn giao hoàn tất.":"Chưa có nhiệm vụ được phân công. Kho cần gán đúng tài khoản shipper; ứng dụng không tự tạo dữ liệu mẫu.");
    }

    private void taskDetail(JSONObject task) {
        button("Quay về danh sách",()->{activeId="";render();},true);
        title(task.optString("code")); label(task.optString("warehouseName"));
        label(status(task.optString("status"))+" · Phiên "+task.optInt("version"));
        List<String> packages=strings(task.optJSONArray("packages"));
        HashSet<String> scanned=new HashSet<>(strings(task.optJSONArray("scannedCodes")));
        note("Đã đối chiếu "+scanned.size()+" / "+packages.size()+" kiện theo dữ liệu máy chủ.");
        for(String code:packages) label((scanned.contains(code)?"✓  ":"○  ")+code);
        boolean ready=task.optString("status").equals("ready_for_handover");
        boolean accepted=task.optBoolean("shipperAccepted"), arrived=task.optBoolean("arrivedAtWarehouse");
        boolean mutable=!repository.hasPending();
        if(ready && !accepted) button("Nhận nhiệm vụ",()->act(task,"respond","accepted",true),mutable);
        else if(ready && !arrived) button("Tôi đã đến kho",()->act(task,"arrive",null,null),mutable);
        else if(TaskRules.canScan(task.optString("status"),accepted,arrived)) {
            EditText code=input("Mã kiện","",InputType.TYPE_CLASS_TEXT);
            code.setHint("Nhập mã hoặc dùng đầu đọc mã vạch");
            Button scan=button("Đối chiếu kiện",()->{
                if(code.getText().toString().trim().isEmpty()){code.setError("Nhập mã trên kiện");return;}
                act(task,"scan","package_code",code.getText().toString().trim());
            },mutable);
            code.setImeOptions(EditorInfo.IME_ACTION_DONE);
            code.setOnEditorActionListener((v,action,event)->{if(action==EditorInfo.IME_ACTION_DONE){scan.performClick();return true;}return false;});
            boolean full=TaskRules.canConfirm(task.optString("status"),accepted,arrived,packages,scanned);
            button("Xác nhận nhận hàng",()->new AlertDialog.Builder(this).setTitle("Xác nhận nhận hàng?")
                .setMessage("Bạn đã kiểm tra đủ các kiện. Kho vẫn cần xác nhận để hoàn tất bàn giao và ghi xuất tồn.")
                .setNegativeButton("Kiểm tra lại",null).setPositiveButton("Xác nhận",(dialog,which)->act(task,"shipper-confirm",null,null)).show(),mutable && full);
            if(!full)label("Cần đối chiếu đủ mã kiện trước khi xác nhận.");
        } else if(!ready) note(task.optString("status").equals("handed_over")?"Kho đã hoàn tất bàn giao.":"Đã gửi xác nhận shipper; đang chờ kho xác nhận. Tải lại để cập nhật.");
        label("Đối chiếu hiện hỗ trợ nhập mã/đầu đọc bàn phím; chưa tích hợp camera.");
    }

    private void act(JSONObject task,String action,String name,Object value) {
        request(()->{
            JSONObject payload=new JSONObject().put("version",task.getInt("version"));
            if(name!=null)payload.put(name,value);
            return repository.act(task.getString("id"),action,payload);
        },this::acceptTask);
    }

    private void acceptTask(JSONObject result) {
        boolean found=false;
        for(int i=0;i<tasks.size();i++)if(tasks.get(i).optString("id").equals(result.optString("id"))){tasks.set(i,result);found=true;break;}
        if(!found)tasks.add(result); activeId=result.optString("id");
        message=result.optString("status").equals("pending_confirmations")?"Shipper đã xác nhận. Đang chờ kho xác nhận.":"Máy chủ đã ghi nhận thao tác.";
    }

    private void account() {
        label("Tài khoản: "+repository.profile().optString("username"));label("Vai trò: SHIPPER");label("Máy chủ: "+server);
        label("Ứng dụng chỉ đọc nhiệm vụ được phân cho tài khoản này. Dữ liệu PostgreSQL được xử lý qua API, không kết nối database trực tiếp.");
        button("Đăng xuất",()->new AlertDialog.Builder(this).setTitle("Đăng xuất?")
            .setMessage("Phiên và lệnh chờ trên thiết bị sẽ được xóa. Lệnh chưa rõ kết quả cần kiểm tra lại trên máy chủ khi đăng nhập.")
            .setNegativeButton("Hủy",null).setPositiveButton("Đăng xuất",(d,w)->request(()->{repository.logout();return true;},ok->{tasks.clear();activeId="";message="Đã đăng xuất.";})).show(),true);
    }

    private <T> void request(Callable<T> work,Consumer<T> success) {
        if(busy)return; busy=true; message="Đang kết nối máy chủ…"; render();
        network.execute(()->{
            T result=null; Exception failure=null;
            try{result=work.call();}catch(Exception e){failure=e;}
            final T value=result; final Exception error=failure;
            runOnUiThread(()->{
                if(isFinishing()||isDestroyed())return; busy=false;
                if(error==null)success.accept(value);
                else if(error instanceof ApiException && ((ApiException)error).status==401){
                    repository.clear();tasks.clear();activeId="";message="Phiên hết hạn hoặc thông tin đăng nhập không đúng. Hãy đăng nhập lại.";
                } else if(error instanceof IOException){
                    message=repository!=null && repository.hasPending()?"Mất kết nối/chưa rõ kết quả. Hãy thử lại cùng lệnh, không giả định đã thành công.":"Không kết nối được máy chủ. Kiểm tra địa chỉ, Wi-Fi/USB và backend đang chạy.";
                } else message=error.getMessage()==null?"Không thực hiện được thao tác.":error.getMessage();
                render();
            });
        });
    }

    private void navigation() {
        LinearLayout bar=new LinearLayout(this);bar.setBackgroundColor(Color.WHITE);bar.setPadding(dp(4),dp(6),dp(4),dp(6));
        for(String name:new String[]{"Nhiệm vụ","Quét mã","Lịch sử","Tài khoản"}){
            Button b=new Button(this);b.setText(name);b.setAllCaps(false);b.setTextSize(12);b.setTextColor(tab.equals(name)?ORANGE:MUTED);
            b.setMinWidth(0);b.setPadding(0,0,0,0);b.setEnabled(!busy);b.setOnClickListener(v->{tab=name;message="";render();});
            bar.addView(b,new LinearLayout.LayoutParams(0,dp(56),1));
        }
        root.addView(bar);
    }

    private List<String> strings(JSONArray array){List<String> result=new ArrayList<>();if(array!=null)for(int i=0;i<array.length();i++)result.add(array.optString(i));return result;}
    private String status(String value){return value.equals("handed_over")?"Đã bàn giao":value.equals("pending_confirmations")?"Chờ kho xác nhận":"Sẵn sàng bàn giao";}
    private TextView text(String value,int size,int color,boolean bold){TextView v=new TextView(this);v.setText(value);v.setTextSize(size);v.setTextColor(color);if(bold)v.setTypeface(null,Typeface.BOLD);v.setPadding(0,dp(6),0,dp(6));return v;}
    private void title(String value){content.addView(text(value,24,INK,true));}
    private void label(String value){content.addView(text(value,15,MUTED,false));}
    private void note(String value){TextView v=text(value,15,INK,false);v.setPadding(dp(14),dp(12),dp(14),dp(12));GradientDrawable bg=new GradientDrawable();bg.setColor(0xfffff7ed);bg.setCornerRadius(dp(10));v.setBackground(bg);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(8),0,dp(12));content.addView(v,p);}
    private EditText input(String label,String value,int type){label(label);EditText v=new EditText(this);v.setText(value);v.setTextSize(16);v.setTextColor(INK);v.setInputType(type);v.setSingleLine(true);v.setSaveEnabled(false);v.setEnabled(!busy);v.setContentDescription(label);content.addView(v,new LinearLayout.LayoutParams(-1,dp(52)));return v;}
    private Button makeButton(String value,Runnable action,boolean enabled){Button b=new Button(this);b.setText(value);b.setAllCaps(false);b.setTextSize(16);b.setTextColor(Color.WHITE);GradientDrawable bg=new GradientDrawable();bg.setColor(ORANGE);bg.setCornerRadius(dp(10));b.setBackground(bg);b.setMinHeight(dp(50));b.setEnabled(!busy&&enabled);b.setAlpha(b.isEnabled()?1f:0.4f);b.setOnClickListener(v->action.run());LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(10),0,dp(8));b.setLayoutParams(p);return b;}
    private Button button(String value,Runnable action,boolean enabled){Button b=makeButton(value,action,enabled);content.addView(b);return b;}
    private LinearLayout card(){LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);c.setPadding(dp(16),dp(12),dp(16),dp(12));GradientDrawable bg=new GradientDrawable();bg.setColor(Color.WHITE);bg.setCornerRadius(dp(12));bg.setStroke(dp(1),0xffe2e8f0);c.setBackground(bg);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(12),0,dp(8));content.addView(c,p);return c;}
    @Override protected void onDestroy(){network.shutdown();if(isFinishing()&&repository!=null)repository.clear();super.onDestroy();}
}
