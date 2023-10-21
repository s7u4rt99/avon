import React from "react";
import { Pressable, StyleSheet, useColorScheme } from "react-native";
import { TouchableOpacity, TouchableOpacityProps } from "react-native";
import * as Haptics from "expo-haptics";

interface ButtonProps extends TouchableOpacityProps {
  children?: React.ReactNode;
}

export default function StyledButton(props: ButtonProps) {
  const colorScheme = useColorScheme();
  return (
    <Pressable>
      {(pressedProps) => (
        <TouchableOpacity
          {...props}
          style={[
            props.style,
            styles.styledButton,
            {
              backgroundColor: pressedProps.pressed
                ? "#262626"
                : colorScheme === "dark"
                ? "#262626"
                : "#fff",
            },
          ]}
          onPress={(e) => {
            props.onPress && props.onPress(e);
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          }}
          onLongPress={(e) => {
            props.onLongPress && props.onLongPress(e);
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          }}
        />
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  styledButton: {
    padding: "5%",
    borderRadius: 20,
    shadowOpacity: 0.5,
    shadowOffset: {
      width: 0,
      height: 0,
    },
    textShadowColor: "#fff",
  },
});
