import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { CodeEditor, CodeEditorProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StCodeEditor({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    value = "",
    language = "javascript",
    editorTheme = "light",
    height = "300px",
    width = "100%",
    options,
    label,
    onCopy,
    onLaunch,
    ...codeEditorProps
  } = args as {
    name?: string
    value?: string
    language?: string
    editorTheme?: CodeEditorProps["theme"]
    height?: string | number
    width?: string | number
    options?: Record<string, unknown>
    label?: string
    onCopy?: (code: string) => void
    onLaunch?: (code: string) => void
  } & Partial<CodeEditorProps>

  // Handle code changes and send back to Streamlit
  const handleChange = (newValue: string | undefined) => {
    const updatedValue = newValue || ""
    Streamlit.setComponentValue({
      value: updatedValue,
      name: name || "code_editor",
    })
  }

  // setFrameHeight should be called on first render and evertime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge code editor props
  const mergedCodeEditorProps = {
    value,
    onChange: handleChange,
    language,
    theme: editorTheme,
    height,
    width,
    options,
    label,
    onCopy,
    onLaunch,
    disabled: disabled || codeEditorProps.disabled,
    ...codeEditorProps,
  }

  return <CodeEditor {...mergedCodeEditorProps} />
}

export default withStreamlitConnection(StCodeEditor)
