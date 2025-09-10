import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Input, InputProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StInput({ args, disabled, theme }: ComponentProps<any>): ReactElement {
  const {
    name,
    value = "",
    placeholder = "Enter text...",
    size = "small",
    iconLeft,
    iconRight,
    error = false,
    type = "text",
    ...inputProps
  } = args as {
    name?: string
    value?: string
    placeholder?: string
    size?: InputProps["size"]
    iconLeft?: React.ReactNode
    iconRight?: React.ReactNode
    error?: boolean
    type?: string
  } & Partial<InputProps>

  // Handle input changes and send back to Streamlit
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    Streamlit.setComponentValue({
      value: e.target.value,
      name: name || "input",
    })
  }

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge input props
  const mergedInputProps = {
    value,
    placeholder,
    size,
    iconLeft,
    iconRight,
    error,
    type,
    onChange: handleChange,
    disabled: disabled || inputProps.disabled,
    ...inputProps,
  }

  return <Input {...mergedInputProps} />
}

export default withStreamlitConnection(StInput)
