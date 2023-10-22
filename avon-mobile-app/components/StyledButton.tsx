import React, { forwardRef } from "react";
import { Pressable, StyleSheet, useColorScheme } from "react-native";
import { TouchableOpacity, TouchableOpacityProps } from "react-native";
import * as Haptics from "expo-haptics";

interface ButtonProps extends TouchableOpacityProps {
  children?: React.ReactNode;
}

function StyledButton(props: ButtonProps, ref: React.Ref<TouchableOpacity>) {
  const colorScheme = useColorScheme();
  return (
    <Pressable>
      {(pressedProps) => (
        <TouchableOpacity
          {...props}
          ref={ref}
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
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          }}
          onLongPress={(e) => {
            props.onLongPress && props.onLongPress(e);
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
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

export default forwardRef(StyledButton);
