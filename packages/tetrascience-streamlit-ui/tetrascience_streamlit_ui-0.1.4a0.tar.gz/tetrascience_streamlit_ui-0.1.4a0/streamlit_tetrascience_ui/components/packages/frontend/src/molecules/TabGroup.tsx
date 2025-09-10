import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { TabGroup, TabGroupProps, TabItem } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StTabGroup({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    tabs = [],
    activeTab,
    size = "medium",
    ...tabGroupProps
  } = args as TabGroupProps

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      activeTab,
    })
  }, [activeTab])

  const mergedTabGroupProps = {
    tabs,
    activeTab,
    size,
    ...tabGroupProps,
  }

  return <TabGroup {...mergedTabGroupProps} />
}

export default withStreamlitConnection(StTabGroup) 