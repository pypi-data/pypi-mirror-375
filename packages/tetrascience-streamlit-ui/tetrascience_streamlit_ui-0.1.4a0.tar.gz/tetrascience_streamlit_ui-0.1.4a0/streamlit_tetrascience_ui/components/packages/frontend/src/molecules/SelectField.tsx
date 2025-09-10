import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { SelectField, SelectFieldProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StSelectField({
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
    ...dropdownProps
  } = args as SelectFieldProps

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      label,
    })
  }, [label])

  const mergedSelectFieldProps = {
    label,
    infoText,
    supportiveText,
    showSupportiveCheck,
    className,
    ...dropdownProps,
  }

  return <SelectField {...mergedSelectFieldProps} />
}

export default withStreamlitConnection(StSelectField) 