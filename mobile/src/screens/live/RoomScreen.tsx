/**
 * Live room screen with video and chat.
 * Note: This is a simplified version. Full LiveKit integration requires additional setup.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { api } from '../../services/api';
import { LiveRoom, LiveRoomMessage } from '../../types';

export default function RoomScreen({ route, navigation }: any) {
  const { roomId, isHost = false } = route.params;
  const [room, setRoom] = useState<LiveRoom | null>(null);
  const [messages, setMessages] = useState<LiveRoomMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoom();
    loadMessages();
    // Poll for new messages (in production, use WebSocket)
    const interval = setInterval(loadMessages, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadRoom = async () => {
    try {
      const data = await api.getRoom(roomId);
      setRoom(data);

      if (!isHost) {
        // Join as viewer and get token
        const token = await api.joinRoom(roomId);
        // In production: Initialize LiveKit with token.token and token.ws_url
        console.log('LiveKit token:', token);
      }
    } catch (error) {
      Alert.alert('Hata', 'Yayın yüklenemedi');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async () => {
    try {
      const data = await api.getRoomMessages(roomId);
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      await api.sendRoomMessage(roomId, newMessage);
      setNewMessage('');
      loadMessages();
    } catch (error) {
      Alert.alert('Hata', 'Mesaj gönderilemedi');
    }
  };

  const handleEndRoom = async () => {
    Alert.alert(
      'Yayını Bitir',
      'Yayını bitirmek istediğinizden emin misiniz?',
      [
        { text: 'İptal', style: 'cancel' },
        {
          text: 'Bitir',
          style: 'destructive',
          onPress: async () => {
            try {
              await api.endRoom(roomId);
              navigation.goBack();
            } catch (error) {
              Alert.alert('Hata', 'Yayın bitirilemedi');
            }
          },
        },
      ]
    );
  };

  if (loading || !room) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Yükleniyor...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Video placeholder - Replace with LiveKit video component */}
      <View style={styles.videoContainer}>
        <Text style={styles.videoPlaceholder}>
          📹 Video Stream
          {'\n'}
          (LiveKit integration required)
        </Text>
        <View style={styles.videoOverlay}>
          <View style={styles.liveTag}>
            <Text style={styles.liveTagText}>🔴 CANLI</Text>
          </View>
          <Text style={styles.roomTitle}>{room.title}</Text>
        </View>
      </View>

      {/* Chat */}
      <View style={styles.chatContainer}>
        <FlatList
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.message}>
              <Text style={styles.messageAuthor}>
                {item.user.display_name}:
              </Text>
              <Text style={styles.messageText}>{item.message_text}</Text>
            </View>
          )}
        />

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="Mesaj yaz..."
            placeholderTextColor="#666"
            value={newMessage}
            onChangeText={setNewMessage}
          />
          <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage}>
            <Text style={styles.sendButtonText}>Gönder</Text>
          </TouchableOpacity>
        </View>

        {isHost && (
          <TouchableOpacity style={styles.endButton} onPress={handleEndRoom}>
            <Text style={styles.endButtonText}>Yayını Bitir</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity
          style={styles.shopButton}
          onPress={() => navigation.navigate('Shop')}
        >
          <Text style={styles.shopButtonText}>🛒 MissYak Mağaza</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
  },
  videoContainer: {
    height: 250,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  videoPlaceholder: {
    color: '#666',
    fontSize: 16,
    textAlign: 'center',
  },
  videoOverlay: {
    position: 'absolute',
    top: 10,
    left: 10,
    right: 10,
  },
  liveTag: {
    backgroundColor: '#ff0000',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  liveTagText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  roomTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 10,
  },
  chatContainer: {
    flex: 1,
    padding: 15,
  },
  message: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  messageAuthor: {
    color: '#ff6b35',
    fontWeight: 'bold',
    marginRight: 5,
  },
  messageText: {
    color: '#fff',
    flex: 1,
  },
  inputContainer: {
    flexDirection: 'row',
    marginTop: 10,
  },
  input: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    color: '#fff',
    borderRadius: 8,
    padding: 10,
    marginRight: 10,
  },
  sendButton: {
    backgroundColor: '#ff6b35',
    borderRadius: 8,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  endButton: {
    backgroundColor: '#ff0000',
    borderRadius: 8,
    padding: 12,
    marginTop: 10,
    alignItems: 'center',
  },
  endButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  shopButton: {
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 12,
    marginTop: 10,
    alignItems: 'center',
  },
  shopButtonText: {
    color: '#ff6b35',
    fontWeight: 'bold',
  },
});
