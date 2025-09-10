import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { FormField, FormFieldProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StFormField({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    label,
    infoText,
    supportiveText,
    showSupportiveCheck = false,
    className,
    ...inputProps
  } = args as FormFieldProps

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      label,
    })
  }, [label])

  const mergedFormFieldProps = {
    label,
    infoText,
    supportiveText,
    showSupportiveCheck,
    className,
    ...inputProps,
  }

  return <FormField {...mergedFormFieldProps} />
}

export default withStreamlitConnection(StFormField) 