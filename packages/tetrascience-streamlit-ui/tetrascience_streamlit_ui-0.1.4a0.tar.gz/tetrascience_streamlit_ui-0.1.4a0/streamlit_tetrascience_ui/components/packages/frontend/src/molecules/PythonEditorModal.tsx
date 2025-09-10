import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { PythonEditorModal, PythonEditorModalProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StPythonEditorModal({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    open,
    initialValue = "",
    title = "",
    ...pythonEditorModalProps
  } = args as PythonEditorModalProps

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      open,
      title,
    })
  }, [open, title])

  const mergedPythonEditorModalProps = {
    open,
    initialValue,
    title,
    ...pythonEditorModalProps,
  }

  return <PythonEditorModal {...mergedPythonEditorModalProps} />
}

export default withStreamlitConnection(StPythonEditorModal) 