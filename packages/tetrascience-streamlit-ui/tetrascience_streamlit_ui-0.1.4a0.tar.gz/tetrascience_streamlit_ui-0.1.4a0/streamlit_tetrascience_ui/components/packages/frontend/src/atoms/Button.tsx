import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Button, ButtonProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StButton({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    label = "Click Me!",
    variant = "primary",
    size = "small",
    ...buttonProps
  } = args as {
    name?: string
    label?: string
    variant?: ButtonProps["variant"]
    size?: ButtonProps["size"]
  } & Partial<ButtonProps>

  // setFrameHeight should be called on first render and evertime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge the onClick handler with any provided onClick prop
  const mergedButtonProps = {
    variant,
    size,
    ...buttonProps,
    onClick: (e: React.MouseEvent<HTMLButtonElement>) => {
      if (buttonProps.onClick) {
        buttonProps.onClick(e)
      }
    },
    disabled: disabled || buttonProps.disabled,
  }

  return <Button {...mergedButtonProps}>{label}</Button>
}

export default withStreamlitConnection(StButton)
