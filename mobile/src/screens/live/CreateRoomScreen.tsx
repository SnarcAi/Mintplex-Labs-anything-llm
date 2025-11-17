/**
 * Create live room screen.
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
} from 'react-native';
import { api } from '../../services/api';

export default function CreateRoomScreen({ navigation }: any) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!title.trim()) {
      Alert.alert('Hata', 'Lütfen yayın başlığı girin');
      return;
    }

    setLoading(true);
    try {
      const room = await api.createRoom(title, description);
      // Start the room immediately
      await api.startRoom(room.id);
      // Navigate to room screen
      navigation.replace('Room', { roomId: room.id, isHost: true });
    } catch (error: any) {
      Alert.alert('Hata', 'Yayın oluşturulamadı');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Yayın Başlığı *</Text>
      <TextInput
        style={styles.input}
        placeholder="Örn: Akşam Balık Keyfi"
        placeholderTextColor="#666"
        value={title}
        onChangeText={setTitle}
      />

      <Text style={styles.label}>Açıklama</Text>
      <TextInput
        style={[styles.input, styles.textArea]}
        placeholder="Yayınınız hakkında bilgi verin..."
        placeholderTextColor="#666"
        value={description}
        onChangeText={setDescription}
        multiline
        numberOfLines={4}
      />

      <TouchableOpacity
        style={styles.button}
        onPress={handleCreate}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Yayını Başlat</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 20,
  },
  label: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 8,
    marginTop: 15,
  },
  input: {
    backgroundColor: '#2a2a2a',
    color: '#fff',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  button: {
    backgroundColor: '#ff6b35',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginTop: 30,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
