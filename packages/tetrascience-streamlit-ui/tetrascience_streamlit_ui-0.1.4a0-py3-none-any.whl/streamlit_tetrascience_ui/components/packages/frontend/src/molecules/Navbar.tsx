import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { Navbar, NavbarProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

function StNavbar({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const { organization, ...navbarProps } = args as NavbarProps

  useEffect(() => {
    Streamlit.setFrameHeight(80)
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      organization,
    })
  }, [organization])

  const mergedNavbarProps = {
    organization,
    ...navbarProps,
  }

  return <Navbar {...mergedNavbarProps} />
}

export default withStreamlitConnection(StNavbar)
