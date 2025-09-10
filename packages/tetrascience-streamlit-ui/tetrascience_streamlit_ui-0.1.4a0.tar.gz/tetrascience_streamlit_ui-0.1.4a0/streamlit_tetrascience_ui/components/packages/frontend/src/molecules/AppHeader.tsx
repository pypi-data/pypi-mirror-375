import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { AppHeader, AppHeaderProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

function StAppHeader({
  args,
  theme,
}: ComponentProps<any>): ReactElement {
  const { hostname, userProfile, ...appHeaderProps } = args as AppHeaderProps

  useEffect(() => {
    Streamlit.setFrameHeight(65)
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      hostname,
      userProfile,
    })
  }, [hostname, userProfile])

  const mergedAppHeaderProps = {
    hostname,
    userProfile,
    ...appHeaderProps,
  }

  return <AppHeader {...mergedAppHeaderProps} />
}

export default withStreamlitConnection(StAppHeader)
