import React, { useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  View,
  Text,
  TextInput,
  ActivityIndicator,
  Pressable,
  Platform,
  useWindowDimensions,
  StyleSheet,
} from "react-native";
import Slider from "@react-native-community/slider";
import { Picker } from "@react-native-picker/picker";


type Interests = Record<"adventure" | "culture" | "relaxation" | "food", boolean>;
type Recommendation = {
  name: string;
  description: string;
  reason: string;
  satisfaction_score: number;
};
const PINK = "#FA3A6E";


export default function HomeScreen() {
  const { width } = useWindowDimensions();
  const isWide = width > 820;

  const [climate, setClimate] = useState<"tropical" | "cold" | "moderate">("tropical");
  const [duration, setDuration] = useState("5");
  const [budget, setBudget] = useState(2000);
  const [interests, setInterests] = useState<Interests>({
    adventure: false,
    culture: false,
    relaxation: false,
    food: false,
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Recommendation[]>([]);

  const toggleInterest = (k: keyof Interests) =>
    setInterests((prev) => ({ ...prev, [k]: !prev[k] }));

  const onSubmit = async () => {
    const chosen = (Object.entries(interests) as [keyof Interests, boolean][])
      .filter(([, v]) => v)
      .map(([k]) => k);

    setLoading(true);
    try {
      const baseUrl =
        Platform.OS === "android" ? "http://10.0.2.2:8000" : "http://127.0.0.1:8000";
      const res = await fetch(`${baseUrl}/api/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ climate, duration: +duration, budget, interests: chosen }),
      });
      const json = await res.json();
      setResults(json.recommendations || []);
    } catch {
      alert("Error fetching recommendations");
    } finally {
      setLoading(false);
    }
  };


  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View
          style={[
            styles.formWrapper,
            isWide ? styles.formWrapperWide : styles.formWrapperNarrow,
          ]}
        >
          <Text style={styles.heading}>Plan Your Trip</Text>


          <View style={styles.field}>
            <Text style={styles.label}>Preferred Climate</Text>
            <View style={styles.pickerWrapper}>
              <Picker selectedValue={climate} onValueChange={(v) => setClimate(v as any)}>
                <Picker.Item label="Tropical" value="tropical" />
                <Picker.Item label="Cold" value="cold" />
                <Picker.Item label="Moderate" value="moderate" />
              </Picker>
            </View>
          </View>


          <View style={styles.field}>
            <Text style={styles.label}>Duration (1–14 days)</Text>
            <TextInput
              style={styles.input}
              keyboardType="number-pad"
              value={duration}
              onChangeText={setDuration}
            />
          </View>


          <View style={styles.field}>
            <Text style={styles.label}>Budget (${budget})</Text>
            <Slider
              minimumValue={500}
              maximumValue={5000}
              step={100}
              value={budget}
              onValueChange={setBudget}
              minimumTrackTintColor={PINK}
              thumbTintColor={PINK}
            />
          </View>


          <Text style={[styles.label, { marginTop: 4 }]}>Interests</Text>
          <View style={styles.interests}>
            {(Object.keys(interests) as Array<keyof Interests>).map((i) => {
              const selected = interests[i];
              return (
                <Pressable
                  key={i}
                  style={({ pressed }) => [
                    styles.interestBtn,
                    {
                      backgroundColor: selected ? PINK : "#eee",
                      opacity: pressed ? 0.8 : 1,
                    },
                  ]}
                  onPress={() => toggleInterest(i)}
                >
                  <Text style={{ color: selected ? "#fff" : "#000" }}>
                    {selected ? `✓ ${i}` : i}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {/* Submit */}
          <Pressable style={styles.submitBtn} onPress={onSubmit}>
            <Text style={styles.submitTxt}>Get Recommendations</Text>
          </Pressable>

          {loading && <ActivityIndicator size="large" color={PINK} />}

          {results.map((r, idx) => (
            <View key={idx} style={styles.card}>
              <Text style={styles.cardTitle}>{r.name}</Text>
              <Text style={styles.cardDesc}>{r.description}</Text>
              <Text style={styles.cardReason}>Why: {r.reason}</Text>
              <Text style={styles.cardScore}>Score: {r.satisfaction_score}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}


const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  scroll: { alignItems: "center", paddingVertical: 24 },


  formWrapper: { width: "90%" },
  formWrapperNarrow: { maxWidth: 420 },
  formWrapperWide: { maxWidth: 600 },

  heading: { fontSize: 28, fontWeight: "bold", marginBottom: 24 },

  field: { marginBottom: 18 },
  label: { fontSize: 16, marginBottom: 6 },

  pickerWrapper: { borderWidth: 1, borderColor: "#ccc", borderRadius: 4 },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 4, padding: 10 },

  interests: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 14 },
  interestBtn: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
  },

  submitBtn: {
    backgroundColor: PINK,
    borderRadius: 30,
    paddingVertical: 14,
    alignItems: "center",
    marginVertical: 28,
  },
  submitTxt: { color: "#fff", fontWeight: "bold" },

  card: {
    padding: 16,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#eee",
    marginBottom: 18,
    backgroundColor: "#fafafa",
  },
  cardTitle: { fontSize: 20, fontWeight: "600" },
  cardDesc: { marginTop: 4 },
  cardReason: { marginTop: 4, fontStyle: "italic" },
  cardScore: { marginTop: 4, fontWeight: "bold" },
});
