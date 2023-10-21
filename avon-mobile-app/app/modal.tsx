import { StatusBar } from 'expo-status-bar';
import { Platform, StyleSheet } from 'react-native';
import React from 'react';

import SettingsModal from '../components/SettingsModal';
import { Text, View } from '../components/Themed';
import { MonoText } from '../components/StyledText';

export default function ModalScreen() {
  return (
    <View style={styles.container}>
      <MonoText style={styles.title}>Settings</MonoText>
      <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      <SettingsModal />

      {/* Use a light status bar on iOS to account for the black space above the modal */}
      <StatusBar style={Platform.OS === 'ios' ? 'light' : 'auto'} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
});