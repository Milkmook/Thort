import android.graphics.Color;
import android.os.AsyncTask;
import android.util.Log;
import androidx.room.Room;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.google.firebase.remoteconfig.FirebaseRemoteConfig;
import com.google.firebase.remoteconfig.FirebaseRemoteConfigSettings;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;

public class Thort {

    private static final String API_URL = "https://api.example.com/language-model";
    private OkHttpClient client;
    private Gson gson;
    private AppDatabase db;
    private DatabaseReference metricsRef;
    private LineChart chart;
    private Map<String, Double> habitTable;
    private List<String> chatHistory;
    private double decayRate = 0.9;

    public Thort(AppDatabase database, DatabaseReference metricsRef, LineChart chart) {
        this.db = database;
        this.metricsRef = metricsRef;
        this.chart = chart;
        this.client = new OkHttpClient();
        this.gson = new Gson();
        this.habitTable = new HashMap<>();
        this.chatHistory = new ArrayList<>();

        // Initialize Firebase Remote Config
        FirebaseRemoteConfig remoteConfig = FirebaseRemoteConfig.getInstance();
        FirebaseRemoteConfigSettings configSettings = new FirebaseRemoteConfigSettings.Builder()
                .setMinimumFetchIntervalInSeconds(3600)
                .build();
        remoteConfig.setConfigSettingsAsync(configSettings);
        remoteConfig.fetchAndActivate();

        // Add ValueEventListener to listen for data changes
        metricsRef.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                // Handle real-time data updates
                for (DataSnapshot snapshot : dataSnapshot.getChildren()) {
                    Metric metric = snapshot.getValue(Metric.class);
                    new InsertMetricTask().execute(metric);
                }
            }

            @Override
            public void onCancelled(DatabaseError databaseError) {
                // Handle errors
            }
        });
    }

    public void processInput(String inputData) {
        chatHistory.add(inputData);
        new GenerateResponseTask().execute(inputData);
    }

    private class GenerateResponseTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... prompts) {
            try {
                return generateResponse(prompts[0]);
            } catch (IOException e) {
                e.printStackTrace();
                return "Error generating response.";
            }
        }

        @Override
        protected void onPostExecute(String response) {
            // Update UI with the response
            Log.d("Thort", "Response: " + response);
        }
    }

    private String generateResponse(String prompt) throws IOException {
        Request request = new Request.Builder()
                .url(API_URL)
                .post(RequestBody.create(MediaType.parse("application/json"), gson.toJson(Map.of("prompt", prompt))))
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) throw new IOException("Unexpected code " + response);

            Type type = new TypeToken<Map<String, String>>() {}.getType();
            Map<String, String> responseMap = gson.fromJson(response.body().string(), type);
            return responseMap.get("response");
        }
    }

    private class InsertMetricTask extends AsyncTask<Metric, Void, Void> {
        @Override
        protected Void doInBackground(Metric... metrics) {
            db.metricDao().insert(metrics[0]);
            return null;
        }

        @Override
        protected void onPostExecute(Void aVoid) {
            new GetMetricsTask().execute();
        }
    }

    private class GetMetricsTask extends AsyncTask<Void, Void, List<Metric>> {
        @Override
        protected List<Metric> doInBackground(Void... voids) {
            return db.metricDao().getAllMetrics();
        }

        @Override
        protected void onPostExecute(List<Metric> metrics) {
            // Update UI with metrics data
            updateChart(metrics);
        }
    }

    private void updateChart(List<Metric> metrics) {
        List<Entry> entries = new ArrayList<>();
        for (int i = 0; i < metrics.size(); i++) {
            entries.add(new Entry(i, (float) metrics.get(i).performance));
        }

        LineDataSet dataSet = new LineDataSet(entries, "Performance");
        dataSet.setColor(Color.BLUE);
        dataSet.setLineWidth(2f);
        dataSet.setCircleColor(Color.RED);
        dataSet.setCircleRadius(6f);
        dataSet.setFillColor(Color.YELLOW);
        dataSet.setMode(LineDataSet.Mode.CUBIC_BEZIER);

        LineData lineData = new LineData(dataSet);
        chart.setData(lineData);
        chart.animateX(2000);
    }
}
