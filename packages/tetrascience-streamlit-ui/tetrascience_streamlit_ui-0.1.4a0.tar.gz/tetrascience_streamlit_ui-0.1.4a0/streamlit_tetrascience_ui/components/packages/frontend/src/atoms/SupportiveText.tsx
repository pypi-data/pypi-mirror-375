import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { SupportiveText, SupportiveTextProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StSupportiveText({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    children = "This is supportive text",
    showCheck = false,
    className,
    ...supportiveTextProps
  } = args as {
    name?: string
    children?: React.ReactNode
    showCheck?: boolean
    className?: string
  } & Partial<SupportiveTextProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge supportive text props
  const mergedSupportiveTextProps = {
    children,
    showCheck,
    className,
    ...supportiveTextProps,
  }

  return <SupportiveText {...mergedSupportiveTextProps} />
}

export default withStreamlitConnection(StSupportiveText)
