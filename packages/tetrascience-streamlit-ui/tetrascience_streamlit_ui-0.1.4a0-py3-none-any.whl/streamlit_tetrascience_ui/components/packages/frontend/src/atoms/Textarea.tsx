import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Textarea, TextareaProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StTextarea({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    placeholder = "Enter text here...",
    value = "",
    size = "small",
    error = false,
    fullWidth = false,
    rows,
    onChange,
    onFocus,
    onBlur,
    ...textareaProps
  } = args as {
    name?: string
    placeholder?: string
    value?: string
    size?: "xsmall" | "small"
    error?: boolean
    disabled?: boolean
    fullWidth?: boolean
    rows?: number
    onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
    onFocus?: (e: React.FocusEvent<HTMLTextAreaElement>) => void
    onBlur?: (e: React.FocusEvent<HTMLTextAreaElement>) => void
  } & Partial<TextareaProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Handle change events and send data back to Streamlit
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (onChange) {
      onChange(e)
    }
    // Send change event back to Streamlit
    Streamlit.setComponentValue({
      event: "change",
      name,
      value: e.target.value,
      placeholder,
    })
  }

  const handleFocus = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    if (onFocus) {
      onFocus(e)
    }
    // Send focus event back to Streamlit
    Streamlit.setComponentValue({
      event: "focus",
      name,
      value: e.target.value,
    })
  }

  const handleBlur = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    if (onBlur) {
      onBlur(e)
    }
    // Send blur event back to Streamlit
    Streamlit.setComponentValue({
      event: "blur",
      name,
      value: e.target.value,
    })
  }

  // Merge textarea props
  const mergedTextareaProps = {
    placeholder,
    value,
    size,
    error,
    disabled,
    fullWidth,
    rows,
    onChange: handleChange,
    onFocus: handleFocus,
    onBlur: handleBlur,
    ...textareaProps,
  }

  return <Textarea {...mergedTextareaProps} />
}

export default withStreamlitConnection(StTextarea)
