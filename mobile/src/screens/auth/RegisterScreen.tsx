/**
 * Registration screen.
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { useAuth } from '../../utils/AuthContext';
import { GrillLevel } from '../../types';

export default function RegisterScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [grillLevel, setGrillLevel] = useState<GrillLevel>(GrillLevel.CAYLAK);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleRegister = async () => {
    if (!email || !password || !displayName) {
      Alert.alert('Hata', 'Lütfen tüm alanları doldurun');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Hata', 'Şifre en az 8 karakter olmalıdır');
      return;
    }

    setLoading(true);
    try {
      await register(email, password, displayName);
    } catch (error: any) {
      Alert.alert('Kayıt Hatası', error.response?.data?.detail || 'Kayıt başarısız');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Kayıt Ol</Text>

      <TextInput
        style={styles.input}
        placeholder="İsim"
        placeholderTextColor="#666"
        value={displayName}
        onChangeText={setDisplayName}
      />

      <TextInput
        style={styles.input}
        placeholder="E-posta"
        placeholderTextColor="#666"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Şifre (min. 8 karakter)"
        placeholderTextColor="#666"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <Text style={styles.label}>Mangal Seviyeniz:</Text>
      <View style={styles.levelContainer}>
        {Object.values(GrillLevel).map((level) => (
          <TouchableOpacity
            key={level}
            style={[
              styles.levelButton,
              grillLevel === level && styles.levelButtonActive,
            ]}
            onPress={() => setGrillLevel(level)}
          >
            <Text
              style={[
                styles.levelText,
                grillLevel === level && styles.levelTextActive,
              ]}
            >
              {level}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity
        style={styles.button}
        onPress={handleRegister}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Kayıt Ol</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 30,
  },
  input: {
    backgroundColor: '#2a2a2a',
    color: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    fontSize: 16,
  },
  label: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 10,
    marginTop: 10,
  },
  levelContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  levelButton: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  levelButtonActive: {
    backgroundColor: '#ff6b35',
  },
  levelText: {
    color: '#888',
    fontSize: 14,
    fontWeight: 'bold',
  },
  levelTextActive: {
    color: '#fff',
  },
  button: {
    backgroundColor: '#ff6b35',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
